#!/usr/bin/env python3
"""Render TRANSFER_BOOTSTRAP.txt from state/.

Usage:  python3 tools/bootstrap.py

The bootstrap is a generated artifact, like index.html. It is the plain-text form
of the same state, so handing it to a new agent gives them exactly what the site
shows - and when the state grows, the bootstrap grows with it.

Run this BEFORE build.py, because build.py embeds the bootstrap in the page.
"""
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'state')


def load(name, default=None):
    p = os.path.join(STATE, name)
    if not os.path.exists(p):
        return default if default is not None else {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


W = 78
def rule(ch='='):
    return ch * W

def hdr(n, title):
    return f"\n{rule()}\nSECTION {n} - {title}\n{rule()}\n"

def wrap(text, indent=''):
    """Wrap to width, preserving the indent."""
    import textwrap
    return textwrap.fill(str(text), width=W - len(indent),
                         initial_indent=indent, subsequent_indent=indent)


def build():
    ws = load('workspace.json')
    canon = load('canon.json')
    laws = load('laws.json')
    fw = load('firewalls.json', {'registry': []})
    contribs = load('contributions.json', {'records': []})
    canon_c = load('canon_contributions.json', {'records': []})
    registry = load('projects_registry.json', {'projects': []})
    log = load('log.json', {'events': []})

    projs = {}
    pdir = os.path.join(STATE, 'projects')
    if os.path.isdir(pdir):
        for fn in os.listdir(pdir):
            if fn.endswith('.json'):
                d = load(os.path.join('projects', fn))
                if d.get('id'):
                    projs[d['id']] = d

    t = ws.get('totals', {})
    O = []
    A = O.append

    A("SOUL LAND UNIVERSAL - TRANSFER BOOTSTRAP")
    A(f"Generated {ws.get('generated','')} from state/. Control Centre is the navigation")
    A("and state reference. Do not hand-edit this file; edit state/ and rebuild.")
    A("")
    A("PURPOSE")
    A(wrap("Transfer active project state to another agent without losing canon "
           "discipline. You are taking over existing projects, not starting a new story."))
    A("")
    A("AT A GLANCE")
    A(f"  projects tracked      {t.get('projects',0)}")
    A(f"  project files         {t.get('files',0):,}")
    A(f"  words on disk         {t.get('words',0):,}")
    A(f"  knowledge firewalls   {len(fw.get('registry',[]))}")
    A(f"  kit laws              {t.get('kit_laws',0)}")
    A(f"  hard gates            {len(laws.get('seven_gates',[]))}")
    A(f"  growth events logged  {len(log.get('events',[]))}")

    # ---- 1 core rule ----
    A(hdr(1, "CORE OPERATING RULE"))
    A("The Control Centre is the navigation and state reference. It is not a drafting")
    A("surface and it is not canon.")
    A("")
    A("- Do not treat author knowledge as character knowledge.")
    A("- Do not invent missing canon.")
    A("- Preserve established decisions unless an explicit authorised change is made.")
    A("- If a source scene is missing, identify it as missing rather than inventing it.")
    A("- Authority order:")
    for i, x in enumerate(laws.get('authority_order', []), 1):
        A(f"    {i}. {x}")

    # ---- 2 pipeline ----
    A(hdr(2, "PIPELINE"))
    stages = laws.get('pipeline', [])
    A(" -> ".join(s.get('stage', '') for s in stages))
    A("")
    for s in stages:
        mark = " [GATE]" if s.get('gate') else ""
        A(wrap(f"{s.get('n'):02d}. {s.get('stage')}{mark} - {s.get('detail')}", '  '))
    A("")
    A("VERIFY and AUDIT are gates. Do not proceed past one until it passes.")
    A("RECORD is never skipped: a decision not written down will regress. In this")
    A("system that means filing it into intake/drop/ as a decision or correction,")
    A("not just saying it in chat.")

    # ---- 3 pre-draft ----
    A(hdr(3, "PRE-DRAFT GATE (six steps, in order)"))
    for s in laws.get('predraft_gate', []):
        A(wrap(f"{s.get('n')}. {s.get('step')} - {s.get('detail')}", ''))
        A("")

    # ---- 4 canon rules ----
    A(hdr(4, "CANON RULES"))
    for r in [
        "Canon first. Butterfly effects must grow from actual changed events.",
        "One canon episode = one operational unit.",
        "Never leak rejected drafts into the active canon.",
        "Never convert suspicion, intuition, rumour, or prophecy fragments into factual character knowledge without evidence.",
        "Do not give characters information earlier than the earliest valid change recorded in their knowledge firewall.",
        "Preserve competent canon characterisation.",
        "Do not nerf or inflate characters merely to force the OC plot.",
        "Record new decisions and corrections so they do not regress later.",
    ]:
        A(wrap("- " + r, '  '))

    # ---- 5 locks ----
    A(hdr(5, "THE TWELVE LOCKS (set before drafting chapter one)"))
    for l in laws.get('twelve_locks', []):
        A(f"  {l.get('n'):2d}. {l.get('lock',''):16s} {l.get('question','')}")
    A("")
    A(wrap("LOCK 4 IS THE ONE THAT MATTERS MOST. " + laws.get('lock_4_rule', ''), ''))

    # ---- 6 gates ----
    A(hdr(6, "THE SEVEN HARD GATES (machine-checked, non-negotiable)"))
    for g in laws.get('seven_gates', []):
        A(wrap(f"{g.get('n')}. {g.get('gate')} - {g.get('why')}", ''))
        A("")
    A("GATE SCOPE - getting this wrong trains everyone to ignore the gate:")
    cols = ['chapters', 'templates', 'law', 'codex', 'audit']
    A(f"  {'gate':34s} " + ' '.join(f"{c[:7]:>8s}" for c in cols))
    for g in laws.get('seven_gates', []):
        sc = g.get('scope', [])
        row = ' '.join(f"{('yes' if c in sc else '-'):>8s}" for c in cols)
        A(f"  {g.get('gate','')[:34]:34s} {row}")
    A("")
    A(wrap(laws.get('gate_scope_warning', ''), ''))
    A("")
    A(wrap(laws.get('self_referential_trap', ''), ''))
    A("")
    A(wrap(laws.get('negative_test_rule', ''), ''))

    # ---- 7 tags ----
    A(hdr(7, "HONESTY TAGS"))
    for tg in canon.get('honesty_tags', []):
        A(f"  {tg.get('tag',''):16s} {tg.get('meaning','')}")
        A(wrap(f"strength: {tg.get('strength','')}", ' ' * 18))

    # ---- 8 canon spine ----
    A(hdr(8, "CANON SPINE (shared across Soul Land projects)"))
    rl = canon.get('rank_ladder', {})
    A(f"RANK LADDER ({rl.get('confidence','')}, {rl.get('sources','')}):")
    rows = rl.get('rows', [])
    half = (len(rows) + 1) // 2
    for i in range(half):
        left = rows[i]
        right = rows[i + half] if i + half < len(rows) else None
        line = f"  {left.get('rank',''):24s} {left.get('levels',''):>8s}"
        if right:
            line += f"    {right.get('rank',''):24s} {right.get('levels',''):>8s}"
        A(line)
    A("")
    A(wrap(rl.get('subdivisions', ''), '  '))
    A(wrap(rl.get('known_error', ''), '  '))
    A("")
    A("RING AGES:")
    for r in canon.get('ring_ages', []):
        note = f"  ({r.get('note')})" if r.get('note') else ''
        A(f"  {r.get('colour',''):8s} {r.get('years'):>10,}   [{r.get('confidence','')}]{note}")
    A("")
    A(wrap(canon.get('optimal_nine_ring', ''), '  '))
    A("")
    bl = canon.get('beast_law', {})
    A(f"BEAST LAW - {bl.get('confidence','').upper()} EVIDENCE, {bl.get('sources','').upper()}:")
    A(wrap(bl.get('warning', ''), '  '))
    for r in bl.get('rows', []):
        A(f"  - {r.get('fact','')}: {r.get('value','')}")
    A("")
    A("USER RULINGS (override all sources):")
    for r in canon.get('user_rulings', []):
        A(wrap(f"- {r.get('topic','')}: {r.get('ruling','')}", '  '))
        if r.get('formula'):
            A(wrap(f"formula: {r.get('formula')}", '    '))
        for f in r.get('forbidden', []):
            A(wrap(f"never: {f}", '    '))
        if r.get('note'):
            A(wrap(f"note: {r.get('note')}", '    '))
    A("")
    A(wrap("FILENAME LAW: " + canon.get('filename_law', ''), ''))

    # ---- 9+ project state ----
    n = 9
    for pid in ['blue_silver', 'sl4_fire_phoenix', 'storyos_naag']:
        p = projs.get(pid)
        if not p:
            continue
        tag = "  [REPORTED - not file-verified]" if p.get('verification') == 'reported' else ""
        A(hdr(n, f"PROJECT STATE: {p.get('name','').upper()}{tag}"))
        n += 1
        A(f"path: {p.get('path','')}")
        A(wrap(f"live edge: {p.get('live_edge','')}", ''))
        auth = p.get('authority')
        if auth:
            A("")
            A("AUTHORITY:")
            for k, v in auth.items():
                A(wrap(f"- {k.replace('_',' ')}: {v}", '  '))
        if pid == 'blue_silver':
            sp = p.get('spine', {})
            A("")
            A(f"SPINE (Lock 4, filled): {sp.get('lock4','')}")
            A(wrap(sp.get('canon_fact_used', ''), '  '))
            A("")
            A("ABSOLUTES:")
            for a in p.get('absolutes', []):
                A(wrap("- " + a, '  '))
            tl = p.get('timeline', {})
            A("")
            A(f"TIMELINE: {tl.get('span','')} = {tl.get('dc_span','')}")
            A(wrap(f"birth anchor: {tl.get('birth_anchor','')}", '  '))
            A(wrap(f"formula: {tl.get('formula','')}", '  '))
            A("")
            A("FIXED ANCHORS:")
            for a in p.get('anchors', []):
                A(f"  year {a.get('year'):>4}  {a.get('anchor',''):32s} {a.get('note','')}")
            cg = p.get('canon_gate', {})
            A("")
            A(wrap(f"CANON GATE - {cg.get('hard_boundary','').upper()}", ''))
            A(wrap(f"Naming {cg.get('naming_dc')} DC. Chapter 15 ends {cg.get('ch15_end_dc')} DC. "
                   f"A Yin's rooted era ends before {cg.get('a_yin_era_ends_before_dc')} DC. "
                   f"Margins +{cg.get('margins',[0,0])[0]} and +{cg.get('margins',[0,0])[1]}.", '  '))
            A(wrap(cg.get('history', ''), '  '))
            A(wrap(cg.get('coda_check', ''), '  '))
            A("")
            A("CULTIVATION: " + '; '.join(
                "~{:,} years at year {}".format(c.get('years', 0), c.get('at_year', '?'))
                for c in p.get('cultivation', [])))
            A(wrap(f"He takes nothing for {p.get('takes_nothing_for','')}.", '  '))
            gl = p.get('ground_language', {})
            A("")
            A(f"GROUND-LANGUAGE - FIXED AT {gl.get('count')} WORDS, LIST CLOSED:")
            A(wrap(', '.join(gl.get('words', [])), '  '))
            A(wrap("11th: " + gl.get('eleventh', ''), '  '))
            A(wrap("delivery chain: " + ' -> '.join(gl.get('delivery_chain', [])), '  '))
            A(wrap(gl.get('point', ''), '  '))
            A("")
            A("THE NAMED HUMANS - he survives by paperwork, not power:")
            for h in p.get('named_humans', []):
                A(wrap(f"- {h.get('name','')} (Ch{h.get('chapter','')}, "
                       f"rings: {h.get('rings') or 'none'}): {h.get('contribution','')}", '  '))
                if h.get('warning'):
                    A(wrap("WARNING: " + h.get('warning'), '    '))
            A("")
            A("DOCUMENTARY CHAIN: " + ' -> '.join(p.get('documentary_chain', [])))
            cu = p.get('the_cull', {})
            A("")
            A(wrap(f"THE CULL: {cu.get('law','')}", ''))
            A(wrap(f"There had been {cu.get('had')}; {cu.get('returned_to_soil')} went back into "
                   f"the soil in single seasons; {cu.get('remain')} remain {cu.get('state','')}, "
                   f"{cu.get('remain_after_746')} after year 746.", '  '))
            ay = p.get('a_yin', {})
            A("")
            A("A YIN:")
            for k in ['appearance', 'age', 'secret', 'act', 'constraint', 'fate']:
                if ay.get(k):
                    A(wrap(f"- {k}: {ay.get(k)}", '  '))
            idn = p.get('identity', {})
            A("")
            A(wrap(f"IDENTITY: {idn.get('is','')} NOT: {', '.join(idn.get('is_not',[]))}.", ''))
            A(wrap(p.get('ending', ''), ''))
        elif pid == 'sl4_fire_phoenix':
            pr = p.get('protagonist', {})
            A("")
            A(f"PROTAGONIST: {pr.get('true_name','')} ({pr.get('true_pronouns','')}), "
              f"cover {pr.get('cover_name','')} ({pr.get('cover_pronouns','')}).")
            A(wrap(f"{pr.get('origin','')}. {pr.get('dorm','')}. {pr.get('reveal_rule','')}", '  '))
            A("")
            A("DO NOT:")
            for d in p.get('do_not', []):
                A(wrap("- " + d, '  '))
            A("")
            A("CURRENT NUMERIC STATUS:")
            for s in p.get('current_status', []):
                A(wrap(f"- {s.get('item','')}: {s.get('value','')} ({s.get('note','')})", '  '))
            cl = p.get('chronology_locks', {})
            A("")
            A("CHRONOLOGY LOCKS:")
            for k, v in cl.items():
                if isinstance(v, list):
                    for x in v:
                        A(wrap("- " + x, '  '))
                else:
                    A(wrap(f"- {k.replace('_',' ')}: {v}", '  '))
            uf = p.get('user_locked_future', {})
            A("")
            A("USER-LOCKED FUTURE:")
            A(wrap(f"- {uf.get('event','')}", '  '))
            A(wrap(f"- awakens: {', '.join(uf.get('awakens',[]))}", '  '))
            A(wrap(f"- aftermath: {uf.get('aftermath','')}", '  '))
            A("")
            A("LATEST CHAPTER RESULTS:")
            for r in p.get('chapter31_results', []):
                A(wrap("- " + r, '  '))
            A("")
            A(wrap("ANTI-NERF: " + p.get('anti_nerf', ''), ''))
        elif pid == 'storyos_naag':
            if p.get('verification_note'):
                A("")
                A(wrap("VERIFICATION: " + p.get('verification_note'), ''))
            A("")
            A(f"UNIVERSE: {p.get('universe','')}")
            A(f"PROTAGONIST: {p.get('protagonist','')}")
            A("")
            A("COUNTS [reported]:")
            for c in p.get('counts', []):
                A(f"  {str(c.get('label','')):28s} {c.get('value','')}")
            if p.get('open_gaps'):
                A("")
                A("OPEN GAPS - FLAG, DO NOT INVENT:")
                for i, g in enumerate(p['open_gaps'], 1):
                    A(wrap(f"{chr(96+i)}. {g.get('question','')}", '  '))
                    A(wrap(g.get('detail', ''), '     '))
                    A(wrap("ruling: " + g.get('ruling', ''), '     '))

    # ---- contributed projects ----
    # These are filed through intake/ rather than living in state/projects/, so
    # they need their own pass or they never reach the transfer document.
    for p in registry.get('projects', []):
        A(hdr(n, f"PROJECT STATE: {p.get('name','').upper()}  [CONTRIBUTED]"))
        n += 1
        A(f"path: {p.get('path','')}")
        A(f"status: {p.get('status','')}")
        A(wrap(f"live edge: {p.get('live_edge','')}", ''))
        if p.get('notes'):
            A(wrap(f"notes: {p.get('notes')}", ''))
        if p.get('verification'):
            A(wrap(f"verification: {p.get('verification')}", ''))
        prov = p.get('provenance', {})
        if prov:
            A(wrap(f"filed by: {prov.get('agent','-')} on {prov.get('date','-')}", ''))
        # surface anything filed against this project so it travels with it
        pid = p.get('id')
        mine_fw = [f for f in fw.get('registry', []) if f.get('project') == pid]
        if mine_fw:
            A("")
            A(f"FIREWALLS ({len(mine_fw)}):")
            for f in mine_fw:
                A(wrap(f"- {f.get('who','')} - {f.get('state','')} - {f.get('topic','')}", '  '))
                A(wrap(f"rule: {f.get('rule','')}", '    '))
        mine_rec = [r for r in contribs.get('records', []) if r.get('project') == pid]
        if mine_rec:
            A("")
            A("RECORDS:")
            for r in mine_rec:
                summary = (r.get('decision') or r.get('text') or r.get('anchor')
                           or r.get('lock') or '-')
                A(wrap(f"- [{r.get('kind','')}] {summary}", '  '))
        A("")

    # ---- firewalls ----
    A(hdr(n, "KNOWLEDGE FIREWALLS"))
    n += 1
    A("STATES: " + ' / '.join(s.get('state', '') for s in laws.get('firewall_states', [])))
    A("")
    A(wrap("Author knowledge is never automatically available to a character.", ''))
    A("")
    for s in laws.get('firewall_states', []):
        A(wrap(f"{s.get('state',''):14s} {s.get('meaning','')} - {s.get('permits','')}", '  '))
    A("")
    A(wrap("THE FOUR LEAK PATHS: " + laws.get('leak_paths', ''), ''))
    A("")
    A(f"THE REGISTRY ({len(fw.get('registry',[]))} firewalls):")
    for f in fw.get('registry', []):
        A(wrap(f"{f.get('id'):2d}. {f.get('who','')} - {f.get('state','')} - {f.get('topic','')}", '  '))
        A(wrap(f"belief: {f.get('belief','')}", '      '))
        A(wrap(f"earliest change: {f.get('earliest_change','')}", '      '))
        A(wrap(f"rule: {f.get('rule','')}", '      '))
    A("")
    A(wrap("HOW TO ADD ONE: " + fw.get('add_rule', ''), ''))

    # ---- adaptation ----
    at = laws.get('adaptation_talent', {})
    A(hdr(n, "ADAPTATION TALENT (cross-project)"))
    n += 1
    A(wrap("WHAT IT IS: " + at.get('is', ''), ''))
    A("")
    A("WHAT IT IS NOT: " + ', '.join(at.get('is_not', [])) + '.')
    A("It has no dialogue, no notifications, no levels, and no narrator.")
    A("")
    A("REQUIREMENTS:")
    for r in at.get('requirements', []):
        A(wrap(f"- {r.get('req','')}: {r.get('detail','')}", '  '))
    A("")
    A(wrap("THE ONE ABUSE TO WATCH FOR: " + at.get('primary_abuse', ''), ''))
    A("")
    A(wrap(at.get('setting_bound', ''), ''))

    # ---- contributions ----
    if canon_c.get('records') or contribs.get('records'):
        A(hdr(n, "CONTRIBUTED STATE"))
        n += 1
        if canon_c.get('records'):
            A("CANON CLAIMS FILED BY AGENTS:")
            for c in canon_c['records']:
                A(wrap(f"- [{c.get('confidence','')}] {c.get('claim','')} "
                       f"(sources: {c.get('sources','-')}; filed by "
                       f"{c.get('provenance',{}).get('agent','-')})", '  '))
            A("")
        if contribs.get('records'):
            A("OTHER RECORDS:")
            for c in contribs['records']:
                summary = (c.get('decision') or c.get('text') or c.get('anchor')
                           or c.get('lock') or '-')
                A(wrap(f"- [{c.get('kind','')}] {summary} "
                       f"(filed by {c.get('provenance',{}).get('agent','-')})", '  '))
            A("")

    # ---- growth protocol ----
    A(hdr(n, "HOW THIS SYSTEM GROWS"))
    n += 1
    A("This is not a static document. It is a generated view over a state layer that")
    A("accepts contributions from any agent.")
    A("")
    A("  FILE      write a JSON contribution into intake/drop/")
    A("  VALIDATE  python3 tools/validate.py intake/drop/<file>.json")
    A("  INGEST    python3 tools/ingest.py intake/drop/<file>.json")
    A("  BUILD     python3 tools/bootstrap.py && python3 tools/build.py")
    A("")
    A("KINDS: " + ', '.join(sorted([
        'project', 'firewall', 'anchor', 'canon', 'lock', 'decision',
        'correction', 'note'])))
    A("")
    A("A firewall contribution needs: who, state, topic, earliest_change, rule.")
    A("A canon contribution needs: claim, confidence - and sources if confidence is")
    A("'canon'. The validator rejects a canon claim with no sources named.")
    A("")
    A("Contributions are APPEND-ONLY. Nothing can silently overwrite existing state;")
    A("a correction is recorded as a correction, keeping the old value visible.")
    A("")
    A("RESERVED: authority_order, seven_gates, gate_scope_warning, _comment. These")
    A("change the shape of the system and need the user, not a contribution.")

    # ---- instructions ----
    A(hdr(n, "INSTRUCTIONS TO THE RECEIVING AGENT"))
    for i, r in enumerate([
        "Ingest this bootstrap fully before doing anything else.",
        "DO NOT immediately draft prose.",
        "First perform LOAD -> VERIFY -> MAP.",
        "State only what is confirmed, what is missing, and what must be reconstructed.",
        "Then use the Control Centre and the project records as the active state.",
        "Do not overwrite established canon, locks, or knowledge firewalls without explicit authorisation.",
        "If a source scene is missing, identify it as missing rather than inventing it.",
        "When continuing, preserve all information-discipline constraints.",
        "Run the seven gates on anything you ship. 'Mostly passing' is a failure.",
        "Record every new decision and correction in the same pass you make it - file it into intake/drop/, do not just say it.",
        "Corrections come before new content.",
    ], 1):
        A(wrap(f"{i:2d}. {r}", ''))
    A("")
    A("END OF TRANSFER BOOTSTRAP")

    out = os.path.join(ROOT, 'TRANSFER_BOOTSTRAP.txt')
    text = '\n'.join(O) + '\n'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    return out, text


if __name__ == '__main__':
    out, text = build()
    print(f"  built {os.path.relpath(out, ROOT)} - "
          f"{len(text):,} chars, {len(text.split()):,} words, "
          f"{text.count(chr(10))+1} lines")
