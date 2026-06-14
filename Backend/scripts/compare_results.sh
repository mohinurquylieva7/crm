#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
#  EduCRM Pro — Load Test Natijalarini Taqqoslash
#  Before (load_test) vs After (stress_test) qiyoslash
#
#  Ishga tushirish:
#    bash scripts/compare_results.sh
#    bash scripts/compare_results.sh --before k6/summary_before.json \
#                                    --after  k6/summary_after.json
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
K6_DIR="$ROOT_DIR/k6"

BEFORE_FILE="$K6_DIR/summary_before.json"
AFTER_FILE="$K6_DIR/summary_after.json"

# Argumentlarni parse qilish
while [[ $# -gt 0 ]]; do
    case "$1" in
        --before) BEFORE_FILE="$2"; shift 2 ;;
        --after)  AFTER_FILE="$2";  shift 2 ;;
        *) echo "Noto'g'ri argument: $1" && exit 1 ;;
    esac
done

# Fayllar mavjudligini tekshirish
[ -f "$BEFORE_FILE" ] || { echo -e "${YELLOW}⚠  Before fayl topilmadi: $BEFORE_FILE${RESET}"; echo "  make load-test ni ishga tushiring"; exit 1; }
[ -f "$AFTER_FILE"  ] || { echo -e "${YELLOW}⚠  After fayl topilmadi: $AFTER_FILE${RESET}";  echo "  make stress-test ni ishga tushiring"; exit 1; }

# python3 bilan taqqoslash
python3 << PYEOF
import json, sys

BEFORE = "$BEFORE_FILE"
AFTER  = "$AFTER_FILE"

def load(path):
    with open(path) as f:
        return json.load(f)

def get(data, *keys, default=0):
    try:
        for k in keys:
            data = data[k]
        return data
    except (KeyError, TypeError):
        return default

before = load(BEFORE)
after  = load(AFTER)

# Metrikalar
def metrics(data):
    m = data.get('metrics', {})
    return {
        'p50':      get(m, 'http_req_duration', 'values', 'p(50)'),
        'p95':      get(m, 'http_req_duration', 'values', 'p(95)'),
        'p99':      get(m, 'http_req_duration', 'values', 'p(99)'),
        'max':      get(m, 'http_req_duration', 'values', 'max'),
        'avg':      get(m, 'http_req_duration', 'values', 'avg'),
        'err_rate': get(m, 'http_req_failed', 'values', 'rate') * 100,
        'rps':      get(m, 'http_reqs', 'values', 'rate'),
        'total':    int(get(m, 'http_reqs', 'values', 'count')),
    }

b = metrics(before)
a = metrics(after)

def delta(old, new, lower_is_better=True):
    if old == 0:
        return "N/A", ""
    pct = ((new - old) / old) * 100
    arrow = "▲" if pct > 0 else "▼"
    if lower_is_better:
        color = "\033[31m" if pct > 10 else ("\033[32m" if pct < -5 else "\033[33m")
    else:
        color = "\033[32m" if pct > 10 else ("\033[31m" if pct < -5 else "\033[33m")
    reset = "\033[0m"
    return f"{arrow}{abs(pct):.1f}%", f"{color}{arrow}{abs(pct):.1f}%{reset}"

BOLD  = "\033[1m"
CYAN  = "\033[36m"
GREEN = "\033[32m"
RESET = "\033[0m"
SEP   = "─" * 60

print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}
{BOLD}{CYAN}║   EduCRM Pro — Load Test Natijalar Taqqoslash            ║{RESET}
{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}
""")

print(f"  {SEP}")
print(f"  {'Metrika':<22} {'Before (C.M3)':>14} {'After (D.M4)':>14} {'Delta':>12}")
print(f"  {SEP}")

rows = [
    ("p50 latency (ms)",  b['p50'],  a['p50'],  True),
    ("p95 latency (ms)",  b['p95'],  a['p95'],  True),
    ("p99 latency (ms)",  b['p99'],  a['p99'],  True),
    ("Max latency (ms)",  b['max'],  a['max'],  True),
    ("Avg latency (ms)",  b['avg'],  a['avg'],  True),
    ("Error rate (%)",    b['err_rate'], a['err_rate'], True),
    ("RPS",               b['rps'],  a['rps'],  False),
    ("Jami so'rovlar",    b['total'], a['total'], False),
]

for name, bval, aval, lib in rows:
    _, colored_delta = delta(bval, aval, lib)
    if isinstance(bval, float):
        print(f"  {name:<22} {bval:>14.1f} {aval:>14.1f} {colored_delta:>12}")
    else:
        print(f"  {name:<22} {bval:>14} {aval:>14} {colored_delta:>12}")

print(f"  {SEP}")

# SLA baholash
print(f"""
  {BOLD}SLA Baholash:{RESET}
  ──────────────────────────────
""")

sla_checks = [
    ("C.M3 p95 < 2000ms",  b['p95'] < 2000,  f"{b['p95']:.0f}ms"),
    ("C.M3 Error < 5%",    b['err_rate'] < 5, f"{b['err_rate']:.2f}%"),
    ("D.M4 p95 < 5000ms",  a['p95'] < 5000,  f"{a['p95']:.0f}ms"),
    ("D.M4 Error < 15%",   a['err_rate'] < 15, f"{a['err_rate']:.2f}%"),
]

all_pass = True
for label, passed, value in sla_checks:
    icon = f"{GREEN}✓{RESET}" if passed else f"\033[31m✗\033[0m"
    status = "O'tdi" if passed else "Muvaffaqiyatsiz"
    print(f"  {icon} {label:<28} {value:>10}  →  {status}")
    if not passed:
        all_pass = False

print()
if all_pass:
    print(f"  {GREEN}{BOLD}Barcha SLA maqsadlariga erishildi! 🎉{RESET}")
else:
    print(f"  \033[31m{BOLD}Ba'zi SLA maqsadlari bajarilmadi. Optimallashtirish kerak.{RESET}")

print(f"""
  {SEP}
  Batafsil natijalar:
    Before: {BEFORE}
    After:  {AFTER}
  {SEP}
""")
PYEOF
