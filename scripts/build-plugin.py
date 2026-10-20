"""Validate and package only distributable plugin sources. Requires Python 3.11+ and PyYAML."""

import argparse
import json
import re
import tempfile
import tomllib
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def package_files():
    files = [ROOT / "plugin.json"]
    for directory in ("skills", "templates", ".codex/agents"):
        base = ROOT / directory
        require(base.is_dir(), f"Missing component directory: {directory}")
        for path in [base, *base.rglob("*")]:
            require(not path.is_symlink() and not getattr(path, "is_junction", lambda: False)(),
                    f"Linked source is not distributable: {path}")
            require(path.resolve().is_relative_to(ROOT), f"Source escapes repository: {path}")
            if path.is_file():
                require(path.suffix in {".md", ".yaml", ".toml"}, f"Unexpected component: {path}")
                files.append(path)
    return sorted(files)


def anchors(text):
    result = set()
    counts = {}
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def validate(files):
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    require(manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "Incorrect plugin schema")
    require(re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", manifest.get("name", ""))
            and len(manifest["name"]) <= 64, "Invalid plugin name")
    require(re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")), "Expected release SemVer")
    require(not {"skills", "mcpServers", "apps", "interface"}.intersection(manifest),
            "Non-portable top-level manifest field")
    interface = manifest["extensions"]["com.openai"]["interface"]
    require(0 < len(interface["shortDescription"]) <= 30, "Invalid listing subtitle length")
    require(isinstance(interface["capabilities"], list), "Capabilities must be an array")
    prompts = interface.get("defaultPrompt")
    require(isinstance(prompts, str) or (isinstance(prompts, list) and 1 <= len(prompts) <= 3
            and all(isinstance(p, str) and p.strip() for p in prompts)), "Invalid default prompts")
    skill_names = []
    for path in (ROOT / "skills").glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8")
        require(path.stat().st_size <= 1024 * 1024, f"Oversized skill: {path}")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        require(match, f"Missing YAML frontmatter: {path}")
        data = yaml.safe_load(match[1])
        require(isinstance(data, dict), f"Invalid skill metadata: {path}")
        require(data.get("name") == path.parent.name and len(data["name"]) <= 64
                and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"]), f"Invalid name: {path}")
        require(isinstance(data.get("description"), str) and data["description"].strip(),
                f"Missing description: {path}")
        skill_names.append(data["name"])
    require(skill_names and len(skill_names) == len(set(skill_names)), "Missing/duplicate skill names")
    included = {p.resolve() for p in files}
    for path in files:
        if path.suffix == ".yaml":
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            require(isinstance(data, dict), f"Invalid YAML object: {path}")
            policy = data.get("policy", {})
            require(not set(policy) - {"products", "allow_implicit_invocation"}, f"Invalid policy: {path}")
            require(policy.get("allow_implicit_invocation") is None
                    or isinstance(policy["allow_implicit_invocation"], bool), f"Invalid invocation: {path}")
        if path.suffix == ".toml":
            tomllib.loads(path.read_text(encoding="utf-8"))
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            ref = urlsplit(link.strip("<>"))
            if ref.scheme or ref.netloc:
                continue
            target = (path.parent / unquote(ref.path)).resolve() if ref.path else path.resolve()
            require(target.is_relative_to(ROOT), f"Link escapes package: {path}: {link}")
            require(target in included or (target.is_dir() and any(p.is_relative_to(target) for p in included)),
                    f"Unpackaged link target: {path}: {link}")
            if ref.fragment:
                require(target.is_file() and unquote(ref.fragment) in anchors(target.read_text(encoding="utf-8")),
                        f"Missing anchor: {path}: {link}")
    return manifest, sorted(skill_names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="ZIP outside the source repository; omit for validation only")
    args = parser.parse_args()
    files = package_files()
    manifest, skills = validate(files)
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(ROOT), "Write archives outside the source repository")
        require(output.suffix.lower() == ".zip", "Output must be a ZIP file")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="codex-workflow-build-") as staging:
            archive = Path(staging) / "plugin.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
                for path in files:
                    z.write(path, path.relative_to(ROOT).as_posix())
            with zipfile.ZipFile(archive) as z:
                require(z.testzip() is None, "Corrupt archive")
                require(set(z.namelist()) == {p.relative_to(ROOT).as_posix() for p in files},
                        "Archive contents differ from validated sources")
                for path in files:
                    require(z.read(path.relative_to(ROOT).as_posix()) == path.read_bytes(),
                            f"Archive content mismatch: {path}")
            # Copy after successful inspection; a failed build does not replace an old artifact.
            import shutil
            shutil.copyfile(archive, output)
        print(f"Archive: {output}")
    print(f"Validated {manifest['name']} {manifest['version']}: {len(files)} files; skills: {', '.join(skills)}")


if __name__ == "__main__":
    main()
