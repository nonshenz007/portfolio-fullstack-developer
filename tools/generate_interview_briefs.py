#!/usr/bin/env python3
"""
Generate INTERVIEW_BRIEF.md for each immediate subfolder (project) in a root directory.

Heuristics-based scanner for:
- Stack & versions (Node/Express/Next, Python/FastAPI/Flask/Django, etc.)
- Entry points and boot flow
- REST/GraphQL endpoints (Express/FastAPI/Flask/Django)
- Frontend routes (Next/React) and major state
- Data models (Prisma/Mongoose/TypeORM/Django/SQL)
- ENV keys & config
- Migrations/tests/CI/Docker

Outputs a structured Markdown brief per project: INTERVIEW_BRIEF.md

No external dependencies; best-effort extraction with TODO notes where unknown.
"""
from __future__ import annotations

import os
import re
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

IGNORE_DIRS = {
    '.git', 'node_modules', '.next', 'build', 'dist', '.venv', 'venv', '.idea', '.cache',
    '.turbo', 'coverage', 'out', '.expo', '.pytest_cache', '__pycache__', '.dart_tool',
}

CODE_EXTS = {'.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.rb', '.php', '.java', '.kt', '.sql'}
MAX_FILES_PER_SCAN = 4000

PREFERRED_DIRS_JS = [
    'src', 'server', 'api', 'routes', 'controllers', 'app', 'pages', 'functions', 'backend', 'services', 'lib'
]
PREFERRED_DIRS_PY = [
    'src', 'app', 'backend', 'api', 'project', 'services'
]
PREFERRED_DIRS_SQL = [
    'db', 'database', 'migrations', 'prisma', 'sql'
]


def debug(msg: str):
    # Lightweight debug log (silent by default). Uncomment to troubleshoot.
    # print(f"[DEBUG] {msg}")
    pass


def read_text_safe(p: Path, max_bytes: int = 2_000_000) -> str:
    try:
        if not p.exists() or not p.is_file():
            return ''
        if p.stat().st_size > max_bytes:
            return ''
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def iter_code_files(project: Path, extensions: Tuple[str, ...], preferred_dirs: List[str]) -> List[Path]:
    files: List[Path] = []
    # Prefer well-known code directories for speed
    for d in preferred_dirs:
        base = project / d
        if not base.exists() or not base.is_dir():
            continue
        for p in base.rglob('*'):
            if len(files) >= MAX_FILES_PER_SCAN:
                return files
            if p.is_file() and p.suffix in extensions and not any(part in IGNORE_DIRS for part in p.parts):
                files.append(p)
    # If too few, scan project root shallowly (depth 2)
    if len(files) < 100:
        for p in project.glob('*'):
            if p.is_file() and p.suffix in extensions and not any(part in IGNORE_DIRS for part in p.parts):
                files.append(p)
            elif p.is_dir() and p.name not in IGNORE_DIRS:
                for q in p.glob('*'):
                    if len(files) >= MAX_FILES_PER_SCAN:
                        return files
                    if q.is_file() and q.suffix in extensions and not any(part in q.parts for part in IGNORE_DIRS):
                        files.append(q)
    return files


def is_project_root(p: Path) -> bool:
    markers = [
        'package.json', 'pyproject.toml', 'requirements.txt', 'go.mod', 'Cargo.toml',
        'composer.json', 'Gemfile', 'pom.xml', 'build.gradle', 'build.gradle.kts',
        'setup.py', 'manage.py', 'next.config.js', 'next.config.ts', 'schema.prisma',
    ]
    for m in markers:
        if (p / m).exists():
            return True
    return False


def list_projects(root: Path) -> List[Path]:
    projects = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith('.'):
            continue
        if name in {'.idea', '.kiro'}:
            continue
        if is_project_root(child):
            projects.append(child)
    return projects


def top_tree(root: Path, depth: int = 2, max_entries: int = 200) -> List[str]:
    lines: List[str] = []
    root_str = root.name
    lines.append(f"{root_str}/")

    def walk(base: Path, level: int):
        if level > depth:
            return
        count = 0
        try:
            entries = sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            return
        for p in entries:
            if count >= max_entries:
                lines.append("  ...")
                return
            if p.name in IGNORE_DIRS or p.name.startswith('.'):
                continue
            rel = p.relative_to(root)
            indent = '  ' * level
            suffix = '/' if p.is_dir() else ''
            lines.append(f"{indent}{rel.name}{suffix}")
            count += 1
            if p.is_dir():
                walk(p, level + 1)

    walk(root, 1)
    return lines


def detect_node(project: Path) -> Dict:
    pkg = project / 'package.json'
    if not pkg.exists():
        return {}
    data = json.loads(read_text_safe(pkg) or '{}')
    deps = data.get('dependencies', {})
    dev_deps = data.get('devDependencies', {})
    scripts = data.get('scripts', {})
    engines = data.get('engines', {})
    node_version = engines.get('node') if isinstance(engines, dict) else None
    stack = []
    if 'next' in deps or 'next' in dev_deps:
        stack.append('Next.js')
    if 'react' in deps or 'react' in dev_deps:
        stack.append('React')
    if 'express' in deps:
        stack.append('Express')
    if 'koa' in deps:
        stack.append('Koa')
    if 'nestjs' in deps or 'nest' in deps:
        stack.append('NestJS')
    if 'typescript' in dev_deps:
        stack.append('TypeScript')
    if 'vite' in dev_deps or 'vite' in deps:
        stack.append('Vite')

    entry_points = []
    if 'main' in data:
        entry_points.append(str(data['main']))
    if 'start' in scripts:
        entry_points.append('npm run start')
    if 'dev' in scripts:
        entry_points.append('npm run dev')
    if 'build' in scripts:
        entry_points.append('npm run build')

    return {
        'pkg': data,
        'stack': stack,
        'scripts': scripts,
        'node_version': node_version,
        'entry_points': entry_points,
    }


def detect_python(project: Path) -> Dict:
    pyproject = project / 'pyproject.toml'
    req = project / 'requirements.txt'
    env = {}
    if not pyproject.exists() and not req.exists():
        return {}
    content = read_text_safe(pyproject) + '\n' + read_text_safe(req)
    stack = []
    if re.search(r'fastapi\b', content, re.I):
        stack.append('FastAPI')
    if re.search(r'flask\b', content, re.I):
        stack.append('Flask')
    if re.search(r'django\b', content, re.I):
        stack.append('Django')
    if re.search(r'uvicorn\b', content, re.I):
        stack.append('Uvicorn')
    # Versions are hard without locking; try pyproject [project] dependencies lines
    return {
        'stack': stack,
        'requirements': read_text_safe(req) if req.exists() else '',
        'pyproject': read_text_safe(pyproject) if pyproject.exists() else '',
    }


def detect_docker_ci(project: Path) -> Dict:
    dockerfile = project / 'Dockerfile'
    compose = project / 'docker-compose.yml'
    gh_workflows = project / '.github' / 'workflows'
    ci = []
    if dockerfile.exists():
        ci.append('Dockerfile')
    if compose.exists():
        ci.append('docker-compose.yml')
    if gh_workflows.exists():
        ci.extend([f'.github/workflows/{p.name}' for p in gh_workflows.glob('*.yml')])
    return {'ci_files': ci}


def find_env_keys(project: Path) -> List[str]:
    keys = set()
    # Collect from .env* templates
    for p in project.glob('.env*'):
        if p.is_file():
            for line in read_text_safe(p).splitlines():
                m = re.match(r'\s*([A-Z0-9_]+)\s*=', line)
                if m:
                    keys.add(m.group(1))
    # Collect from code patterns (capped)
    files_env = iter_code_files(project, ('.js', '.ts', '.jsx', '.tsx'), PREFERRED_DIRS_JS)
    files_env += iter_code_files(project, ('.py',), PREFERRED_DIRS_PY)
    seen = set()
    for p in files_env:
        if str(p) in seen:
            continue
        seen.add(str(p))
        text = read_text_safe(p)
        for m in re.finditer(r'process\.env\.([A-Z0-9_]+)', text):
            keys.add(m.group(1))
        for m in re.finditer(r'os\.getenv\([\'\"]([A-Z0-9_]+)[\'\"]\)', text):
            keys.add(m.group(1))
    return sorted(keys)


def scan_express_endpoints(project: Path) -> List[Dict]:
    routes = []
    pattern_app = re.compile(r'\bapp\.(get|post|put|delete|patch|options|head)\(\s*[\'\"`]([^\'\"`]+)[\'\"`]\s*,', re.I)
    pattern_router = re.compile(r'\brouter\.(get|post|put|delete|patch|options|head)\(\s*[\'\"`]([^\'\"`]+)[\'\"`]', re.I)
    files = iter_code_files(project, ('.js', '.ts', '.jsx', '.tsx'), PREFERRED_DIRS_JS)
    for p in files:
        text = read_text_safe(p)
        if not text:
            continue
        for m in pattern_app.finditer(text):
            method, path = m.group(1).upper(), m.group(2)
            routes.append({'method': method, 'path': path, 'file': str(p.relative_to(project)), 'middleware': 'best-effort', 'handler': 'best-effort'})
        for m in pattern_router.finditer(text):
            method, path = m.group(1).upper(), m.group(2)
            routes.append({'method': method, 'path': path, 'file': str(p.relative_to(project)), 'middleware': 'best-effort', 'handler': 'best-effort'})
    # De-duplicate
    uniq = []
    seen = set()
    for r in routes:
        key = (r['method'], r['path'], r['file'])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def scan_fastapi_flask_django(project: Path) -> List[Dict]:
    routes: List[Dict] = []
    fastapi_pat = re.compile(r'@(app|router)\.(get|post|put|delete|patch|options|head)\(\s*[\'\"`]([^\'\"`]+)[\'\"`]', re.I)
    flask_pat = re.compile(r'@(app|bp)\.route\(\s*[\'\"`]([^\'\"`]+)[\'\"`](?:[^\)]*methods\s*=\s*\[([^\]]+)\])?', re.I)
    django_pat = re.compile(r'\bpath\(\s*[\'\"`]([^\'\"`]+)[\'\"`]\s*,', re.I)
    files = iter_code_files(project, ('.py',), PREFERRED_DIRS_PY)
    for p in files:
        text = read_text_safe(p)
        if not text:
            continue
        for m in fastapi_pat.finditer(text):
            _, method, path = m.groups()
            routes.append({'method': method.upper(), 'path': path, 'file': str(p.relative_to(project)), 'framework': 'FastAPI/Router'})
        for m in flask_pat.finditer(text):
            _, path, methods = m.groups()
            methods_list = []
            if methods:
                methods_list = [s.strip(" ' \"") for s in methods.split(',') if s.strip()]
            if not methods_list:
                methods_list = ['GET']
            for method in methods_list:
                routes.append({'method': method.upper(), 'path': path, 'file': str(p.relative_to(project)), 'framework': 'Flask'})
        if p.name == 'urls.py' or 'django' in (project.name.lower()):
            for m in django_pat.finditer(text):
                path = m.group(1)
                routes.append({'method': 'VARIES', 'path': path, 'file': str(p.relative_to(project)), 'framework': 'Django'})
    # Dedup
    uniq = []
    seen = set()
    for r in routes:
        key = (r['method'], r['path'], r['file'])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def scan_frontend_routes(project: Path) -> List[Dict]:
    routes: List[Dict] = []
    # Next.js: pages/ and app/ routing
    pages = project / 'pages'
    appdir = project / 'app'
    if pages.exists():
        for p in pages.rglob('*'):
            if p.is_file() and p.suffix in {'.js', '.jsx', '.ts', '.tsx'}:
                rel = p.relative_to(project)
                web_path = '/' + str(p.relative_to(pages)).replace('index', '').replace(p.suffix, '')
                web_path = re.sub(r'\\\\|\\\\', '/', web_path)
                web_path = re.sub(r'/+', '/', web_path)
                routes.append({'path': web_path if web_path != '/' else '/', 'component': str(rel)})
    if appdir.exists():
        for p in appdir.rglob('page.*'):
            rel = p.relative_to(project)
            route_dir = str(p.parent.relative_to(appdir))
            web_path = '/' + route_dir if route_dir != '.' else '/'
            routes.append({'path': web_path, 'component': str(rel)})

    # React Router (best effort)
    rr_pat = re.compile(r'<Route\s+path=\{?[\'\"`]([^\'\"`]+)[\'\"`]\}?\s+element=')
    files = iter_code_files(project, ('.js', '.jsx', '.ts', '.tsx'), PREFERRED_DIRS_JS)
    for p in files:
        text = read_text_safe(p)
        if not text:
            continue
        for m in rr_pat.finditer(text):
            routes.append({'path': m.group(1), 'component': str(p.relative_to(project))})
    # Dedup
    uniq = []
    seen = set()
    for r in routes:
        key = (r['path'], r['component'])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def scan_prisma_models(project: Path) -> List[Dict]:
    prisma_dir = project / 'prisma'
    schema = None
    if prisma_dir.exists():
        cand = prisma_dir / 'schema.prisma'
        if cand.exists():
            schema = cand
    if schema is None and (project / 'schema.prisma').exists():
        schema = project / 'schema.prisma'
    models: List[Dict] = []
    if schema and schema.exists():
        text = read_text_safe(schema)
        model_blocks = re.findall(r'model\s+(\w+)\s+\{([\s\S]*?)\}', text, re.M)
        for name, block in model_blocks:
            fields = []
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    fields.append({'name': parts[0], 'type': parts[1], 'raw': line})
            models.append({'name': name, 'fields': fields})
    return models


def scan_mongoose_models(project: Path) -> List[Dict]:
    models: List[Dict] = []
    pat = re.compile(r'new\s+Schema\s*\(\s*\{([\s\S]*?)\}\s*[,\)]', re.M)
    files = iter_code_files(project, ('.js', '.ts'), PREFERRED_DIRS_JS)
    for p in files:
        text = read_text_safe(p)
        if 'mongoose' not in text and 'Schema' not in text:
            continue
        for m in pat.finditer(text):
            body = m.group(1)
            fields = []
            for line in body.splitlines():
                line = line.strip().rstrip(',')
                if not line or line.startswith('//'):
                    continue
                # naive parse: field: Type or field: { type: Type, ... }
                kv = line.split(':', 1)
                if len(kv) == 2:
                    fields.append({'name': kv[0].strip(), 'type': kv[1].strip()})
            models.append({'file': str(p.relative_to(project)), 'fields': fields})
    return models


def scan_django_models(project: Path) -> List[Dict]:
    models: List[Dict] = []
    class_pat = re.compile(r'class\s+(\w+)\(models\.Model\):([\s\S]*?)(?=\nclass\s|\Z)', re.M)
    field_pat = re.compile(r'\s*(\w+)\s*=\s*models\.(\w+)\(')
    files: List[Path] = []
    for d in PREFERRED_DIRS_PY:
        base = project / d
        if base.exists():
            files.extend(list(base.rglob('models.py')))
            if len(files) > MAX_FILES_PER_SCAN:
                break
    if not files:
        files = list(project.rglob('models.py'))[:MAX_FILES_PER_SCAN]
    for p in files:
        text = read_text_safe(p)
        for cls, body in class_pat.findall(text):
            fields = []
            for m in field_pat.finditer(body):
                fields.append({'name': m.group(1), 'type': m.group(2)})
            models.append({'app_models_file': str(p.relative_to(project)), 'model': cls, 'fields': fields})
    return models


def scan_sql_tables(project: Path) -> List[Dict]:
    tables: List[Dict] = []
    pat = re.compile(r'CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_\.\"\`]+)\s*\(([^;]+)\);', re.I | re.M)
    files: List[Path] = []
    for d in PREFERRED_DIRS_SQL:
        base = project / d
        if base.exists():
            files.extend(list(base.rglob('*.sql')))
            if len(files) > MAX_FILES_PER_SCAN:
                break
    if not files:
        files = list(project.rglob('*.sql'))[:MAX_FILES_PER_SCAN]
    for p in files:
        text = read_text_safe(p)
        for _, name, cols in pat.findall(text):
            tables.append({'file': str(p.relative_to(project)), 'name': name, 'definition': cols.strip()[:500]})
    return tables


def detect_tests(project: Path) -> Dict:
    hints = []
    if (project / 'jest.config.js').exists() or (project / 'jest.config.ts').exists():
        hints.append('Jest')
    if (project / 'vitest.config.ts').exists() or (project / 'vitest.config.js').exists():
        hints.append('Vitest')
    if list(project.rglob('pytest.ini')) or list(project.rglob('conftest.py')):
        hints.append('Pytest')
    if list(project.rglob('tests')):
        hints.append('tests/ present')
    return {'test_hints': hints}


def detect_auth_security(project: Path) -> Dict:
    flags = []
    findings = []
    # Node
    files_js = iter_code_files(project, ('.js', '.ts', '.tsx', '.jsx'), PREFERRED_DIRS_JS)
    for p in files_js:
        text = read_text_safe(p)
        if not text:
            continue
        if re.search(r'\bhelmet\b', text):
            findings.append('helmet middleware used')
        if re.search(r'\bcors\b', text) and re.search(r'\bapp\.use\(', text):
            findings.append('CORS configured')
        if re.search(r'\bexpress-rate-limit\b|rateLimit\(', text):
            findings.append('Rate limiting present')
        if re.search(r'jwt|jsonwebtoken', text):
            findings.append('JWT used')
        if re.search(r'passport', text):
            findings.append('Passport auth used')
        if re.search(r'zod|joi|yup', text):
            findings.append('Input validation library present')
    # Python
    files_py = iter_code_files(project, ('.py',), PREFERRED_DIRS_PY)
    for p in files_py:
        text = read_text_safe(p)
        if 'pydantic' in text:
            findings.append('Pydantic models used')
        if re.search(r'fastapi', text) and re.search(r'HTTPBearer|OAuth2PasswordBearer', text):
            findings.append('FastAPI security dependencies present')
    return {'security_findings': sorted(set(findings))}


def detect_entry_points(project: Path, node: Dict, py: Dict) -> List[str]:
    entries = []
    # Node heuristics
    if node:
        entries.extend(node.get('entry_points', []))
        # Common files
        for cand in ['src/index.ts', 'src/index.js', 'server.ts', 'server.js', 'app.ts', 'app.js', 'index.ts', 'index.js']:
            if (project / cand).exists():
                entries.append(cand)
        # Next.js
        if (project / 'next.config.js').exists() or (project / 'next.config.ts').exists():
            entries.append('Next.js app bootstrap via next dev/build')
    # Python heuristics
    if py:
        for cand in ['manage.py', 'app.py', 'main.py', 'src/main.py']:
            if (project / cand).exists():
                entries.append(cand)
    return sorted(set(entries))


def build_snapshot(project: Path, node: Dict, py: Dict) -> Dict:
    stack = []
    versions = []
    build_cmds = []
    if node:
        if node.get('node_version'):
            versions.append(f"node {node['node_version']}")
        stack.extend(node.get('stack', []))
        scripts = node.get('scripts', {})
        if 'build' in scripts:
            build_cmds.append('npm run build')
        if 'start' in scripts:
            build_cmds.append('npm run start')
        if 'dev' in scripts:
            build_cmds.append('npm run dev')
    if py:
        stack.extend(py.get('stack', []))
        # Build/run
        build_cmds.append('pip install -r requirements.txt' if (project / 'requirements.txt').exists() else 'pip install -e . (pyproject)')
        if any((project / f).exists() for f in ['manage.py', 'app.py', 'main.py']):
            build_cmds.append('python manage.py runserver (Django) or uvicorn app:app --reload (FastAPI)')
    return {
        'stack': sorted(set(stack)),
        'versions': versions,
        'build_cmds': sorted(set(build_cmds)),
    }


def format_endpoints_table(endpoints: List[Dict], kind: str = 'REST') -> str:
    if not endpoints:
        return '_None detected_\n'
    lines = [
        f'| METHOD | PATH | Auth? | Handler file | Notes |',
        f'|---|---|---|---|---|',
    ]
    for e in endpoints[:500]:
        method = e.get('method', '')
        path = e.get('path', '')
        file = e.get('file', '')
        notes = e.get('framework', e.get('middleware', ''))
        lines.append(f'| {method} | `{path}` | TODO | `{file}` | {notes} |')
    return '\n'.join(lines) + '\n'


def format_frontend_routes(routes: List[Dict]) -> str:
    if not routes:
        return '_None detected_\n'
    lines = [
        '| PATH | Component |',
        '|---|---|',
    ]
    for r in routes[:500]:
        lines.append(f"| `{r.get('path','')}` | `{r.get('component','')}` |")
    return '\n'.join(lines) + '\n'


def render_md(project: Path, tree_lines: List[str], snapshot: Dict, entry_points: List[str], endpoints_node: List[Dict], endpoints_py: List[Dict], fe_routes: List[Dict], prisma_models: List[Dict], mongoose_models: List[Dict], django_models: List[Dict], sql_tables: List[Dict], env_keys: List[str], docker_ci: Dict, tests: Dict, security: Dict) -> str:
    name = project.name
    tree_md = "```\n" + "\n".join(tree_lines) + "\n```"
    stack = ', '.join(snapshot.get('stack', []) or ['TODO'])
    versions = ', '.join(snapshot.get('versions', []) or [])
    build_cmds = snapshot.get('build_cmds', [])
    build_cmds_md = '\n'.join([f'- `{cmd}`' for cmd in build_cmds]) if build_cmds else '- TODO'
    entry_md = '\n'.join([f'- `{e}`' for e in entry_points]) if entry_points else '- TODO'

    prisma_md = ''
    if prisma_models:
        for m in prisma_models:
            prisma_md += f"- `{m['name']}`: " + ', '.join([f"{f['name']}:{f['type']}" for f in m.get('fields', [])]) + '\n'
    mongoose_md = ''
    if mongoose_models:
        for m in mongoose_models:
            mongoose_md += f"- `{m['file']}` fields: " + ', '.join([f"{f['name']}: {f['type']}" for f in m.get('fields', [])]) + '\n'
    django_md = ''
    if django_models:
        for m in django_models:
            django_md += f"- `{m['model']}` ({m['app_models_file']}): " + ', '.join([f"{f['name']}:{f['type']}" for f in m.get('fields', [])]) + '\n'
    sql_md = ''
    if sql_tables:
        for t in sql_tables:
            sql_md += f"- `{t['name']}` in `{t['file']}`\n"

    env_md = '\n'.join([f'- `{k}`' for k in env_keys]) if env_keys else '- TODO'
    ci_md = '\n'.join([f'- `{c}`' for c in docker_ci.get('ci_files', [])]) if docker_ci.get('ci_files') else '- TODO'
    test_md = '\n'.join([f'- {h}' for h in tests.get('test_hints', [])]) if tests.get('test_hints') else '- TODO'
    sec_md = '\n'.join([f'- {s}' for s in security.get('security_findings', [])]) if security.get('security_findings') else '- TODO'

    md = f"""# {name} — INTERVIEW_BRIEF

1) Snapshot
- Purpose: TODO. Users: TODO. Problem: TODO.
- Stack & versions: {stack}{(' — ' + versions) if versions else ''}
- Build commands:\n{build_cmds_md}
- Entry points & boot:\n{entry_md}

2) Architecture Map
- Folder tree (top 2 levels):
{tree_md}
- Component responsibilities: TODO
- Data flow: request → controller/service → db/cache → response (map with file pointers) — TODO
- External services/APIs: TODO (list and where used)

3) Interfaces
- REST Endpoints (Node/Express etc.):
{format_endpoints_table(endpoints_node)}
- REST Endpoints (FastAPI/Flask/Django):
{format_endpoints_table(endpoints_py)}
- Frontend routes/screens:
{format_frontend_routes(fe_routes)}
- CLI scripts/daemons/crons: TODO

4) Data & Config
- Schemas/Models:
{prisma_md if prisma_md else ''}{mongoose_md if mongoose_md else ''}{django_md if django_md else ''}{sql_md if sql_md else '' if (prisma_md or mongoose_md or django_md or sql_md) else '  - TODO\n'}
- ENV & secrets (keys, purpose, defaults):
{env_md}
- Migrations & seed strategy: TODO

5) Core Logic Deep Dives (best-effort)
- TODO: List 5–10 critical modules with key functions (inputs/outputs/side-effects) and rationale.

6) Reliability, Security, Performance
- Failure modes & graceful handling: TODO
- AuthN/AuthZ, validation, rate limiting, CORS: 
{sec_md}
- Perf notes (N+1 risks, indexing, caching): TODO

7) Deploy & Ops
- Flow Dev → Staging → Prod: TODO
- Docker/CI:
{ci_md}
- Hosting & probes: TODO

8) Testing & QA
- Test framework hints:
{test_md}
- How to run tests: TODO
- Manual test checklist: TODO

9) Interview Q&A
- 12 likely questions with crisp answers referencing this codebase: TODO
- 2 debugging stories, 1 scalability tradeoff, 1 security hardening step: TODO
- 1-week roadmap with impact: TODO

10) Flash Cards (one-liners)
- TODO: 15 concise takeaways (e.g., “CORS configured in X…”, “This index prevents Y…”) 
"""
    return md


def generate_for_project(project: Path):
    try:
        node = detect_node(project)
        py = detect_python(project)
        snapshot = build_snapshot(project, node, py)
        tree_lines = top_tree(project, depth=2)
        endpoints_node = scan_express_endpoints(project)
        endpoints_py = scan_fastapi_flask_django(project)
        fe_routes = scan_frontend_routes(project)
        prisma_models = scan_prisma_models(project)
        mongoose_models = scan_mongoose_models(project)
        django_models = scan_django_models(project)
        sql_tables = scan_sql_tables(project)
        env_keys = find_env_keys(project)
        docker_ci = detect_docker_ci(project)
        tests = detect_tests(project)
        security = detect_auth_security(project)
        entry_points = detect_entry_points(project, node, py)

        md = render_md(
            project,
            tree_lines,
            snapshot,
            entry_points,
            endpoints_node,
            endpoints_py,
            fe_routes,
            prisma_models,
            mongoose_models,
            django_models,
            sql_tables,
            env_keys,
            docker_ci,
            tests,
            security,
        )

        out = project / 'INTERVIEW_BRIEF.md'
        out.write_text(md, encoding='utf-8')
        print(f"✔ Wrote {out}")
    except Exception as e:
        print(f"! Error processing {project}: {e}")
        debug(traceback.format_exc())


def main():
    print(f"Scanning root: {ROOT}")
    filter_arg = os.environ.get('PROJECTS_FILTER', '').strip()
    if filter_arg:
        # Comma-separated names or paths
        targets: List[Path] = []
        for token in [t.strip() for t in filter_arg.split(',') if t.strip()]:
            p = (ROOT / token).resolve() if not token.startswith('/') else Path(token)
            if p.exists() and p.is_dir():
                if is_project_root(p):
                    targets.append(p)
                else:
                    # If not a project root, try its immediate children
                    targets.extend(list_projects(p))
        if not targets:
            print(f"No matching projects for filter '{filter_arg}'.")
            sys.exit(1)
        for p in targets:
            print(f"\n— Generating brief for: {p.name}")
            generate_for_project(p)
        return

    projects = list_projects(ROOT)
    if projects:
        for p in projects:
            print(f"\n— Generating brief for: {p.name}")
            generate_for_project(p)
        return

    # Fallback: treat ROOT itself as a single project
    if is_project_root(ROOT):
        print(f"\n— Generating brief for single project: {ROOT.name}")
        generate_for_project(ROOT)
    else:
        print("No project markers found. Put projects as immediate subfolders of the root.")
        sys.exit(1)


if __name__ == '__main__':
    main()
