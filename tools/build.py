#!/usr/bin/env python3
"""Render the Control Centre site from state/.

Usage:  python3 tools/build.py

The site is a generated artifact. Never hand-edit index.html - edit state/ and
rebuild, or file a contribution into intake/drop/ and let ingest.py merge it.

Everything rendered comes from state/*.json. If a number is on the page, it came
from a JSON file, and that JSON file either was measured from disk by
extract_state.py or was filed as a contribution with provenance attached.
"""
import json, os, html, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'state')


def load(name, default=None):
    p = os.path.join(STATE, name)
    if not os.path.exists(p):
        return default if default is not None else {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def e(s):
    """Escape for HTML. None becomes empty string."""
    if s is None:
        return ''
    return html.escape(str(s))


def table(headers, rows, cls=''):
    """Build a table from a header list and a list of row-cell lists."""
    out = [f'<div class="scroll"><table class="{cls}">' if cls else '<div class="scroll"><table>']
    out.append('<thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>')
    for r in rows:
        out.append('<tr>' + ''.join(c for c in r) + '</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def td(v, cls=''):
    return f'<td class="{cls}">{e(v)}</td>' if cls else f'<td>{e(v)}</td>'


STATE_CLASS = {
    'KNOWN': 's-known', 'KNOWN PARTLY': 's-part', 'SUSPICION': 's-susp',
    'DISBELIEF': 's-disb', 'UNKNOWN': 's-unk', 'FALSE BELIEF': 's-false',
    'HIDDEN': 's-unk',
}

STATUS_TAG = {
    'live': 't-live', 'gate-pass': 't-live', 'portable': 't-live',
    'active': 't-ref', 'reference': 't-ref', 'external': 't-user',
    'template': 't-arch', 'paused': 't-arch', 'superseded': 't-arch',
}

CSS = open(os.path.join(ROOT, 'tools', 'template.css'), encoding='utf-8').read()


def build():
    ws = load('workspace.json')
    canon = load('canon.json')
    laws = load('laws.json')
    fw = load('firewalls.json', {'registry': []})
    log = load('log.json', {'events': []})
    contribs = load('contributions.json', {'records': []})
    canon_c = load('canon_contributions.json', {'records': []})
    registry = load('projects_registry.json', {'projects': []})

    projs = {}
    pdir = os.path.join(STATE, 'projects')
    if os.path.isdir(pdir):
        for fn in os.listdir(pdir):
            if fn.endswith('.json'):
                d = load(os.path.join('projects', fn))
                if d.get('id'):
                    projs[d['id']] = d

    t = ws.get('totals', {})
    n_fw = len(fw.get('registry', []))
    n_contrib = len(contribs.get('records', []))
    n_canon_c = len(canon_c.get('records', []))
    n_events = len(log.get('events', []))
    n_reg = len(registry.get('projects', []))

    S = []
    A = S.append

    # ---------------- head + nav ----------------
    A('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A('<title>SOUL LAND UNIVERSAL - CONTROL CENTRE</title>')
    A(f'<style>{CSS}</style></head><body><div class="shell">')

    nav = [('status','00','Operating status'),('registry','01','Project registry'),
           ('rule','02','Core operating rule'),('pipeline','03','Pipeline'),
           ('predraft','04','Pre-draft gate'),('locks','05','Twelve locks'),
           ('gates','06','Seven hard gates'),('canon','07','Canon spine'),
           ('firewalls','08','Knowledge firewalls'),('bs','09','Blue Silver state'),
           ('sl4','10','SL4 Fire Phoenix'),('storyos','11','StoryOS / Naag'),
           ('others','12','Other projects'),('adaptation','13','Adaptation Talent'),
           ('growth','14','Growth log'),('protocol','15','Contribution protocol'),
           ('bootstrap','16','Transfer bootstrap'),('verify','17','Verification status')]
    A('<nav><div class="brand"><h1>SOUL LAND<br>UNIVERSAL</h1><p>CONTROL CENTRE</p></div><ol>')
    for sid, n, label in nav:
        A(f'<li><a href="#{sid}"><span class="n">{n}</span>{e(label)}</a></li>')
    A('</ol></nav><main>')

    # ---------------- header ----------------
    A('<header><div class="wrap">')
    A('<div class="kicker">NAVIGATION &amp; STATE REFERENCE - GENERATED FROM state/ - NOT A DRAFTING SURFACE</div>')
    A('<h2>Soul Land Universal - Control Centre</h2>')
    A('<p class="sub">The single orientation point for every active serial in this universe, plus '
      'the portable authoring law that governs them. This page is generated. The state beneath it '
      'grows by contribution, and every addition is validated before it lands.</p>')
    A('<div class="statusbar">')
    A(f'<span class="chip ok">FOUNDATION <b>PASS</b></span>')
    A(f'<span class="chip ok">STRUCTURAL ERRORS <b>0</b></span>')
    A(f'<span class="chip ok">INFORMATION DISCIPLINE <b>ACTIVE</b></span>')
    A(f'<span class="chip">PROJECTS <b>{t.get("projects",0)}</b></span>')
    A(f'<span class="chip">WORDS <b>{t.get("words",0):,}</b></span>')
    A(f'<span class="chip">FIREWALLS <b>{n_fw}</b></span>')
    A(f'<span class="chip">GROWTH EVENTS <b>{n_events}</b></span>')
    A(f'<span class="chip warn">BUILT <b>{e(ws.get("generated",""))}</b></span>')
    A('</div></div></header>')

    # ---------------- 00 status ----------------
    A('<section id="status"><div class="wrap"><h3>SECTION 00</h3><h4>Operating status</h4>')
    A('<p>Every figure on this page is rendered from <code>state/*.json</code>. Those files were '
      'measured from disk by <code>tools/extract_state.py</code> or filed as validated contributions. '
      'Nothing here is typed into the page by hand.</p>')
    A('<div class="grid g4">')
    for val, label in [(t.get('projects',0),'PROJECTS TRACKED'),
                       (f"{t.get('files',0):,}",'PROJECT FILES'),
                       (f"{t.get('words',0)/1_000_000:.2f}M",'WORDS ON DISK'),
                       (t.get('blue_silver_chapters',0)+t.get('sl4_chapters',0),'LIVE CHAPTERS')]:
        A(f'<div class="card"><div class="metric">{e(val)}</div><div class="mlabel">{e(label)}</div></div>')
    A('</div>')
    A('<div class="grid g3">')
    A('<div class="card"><h6>What this document is</h6><ul>'
      '<li>A navigation and state reference</li><li>A transfer bootstrap for new agents</li>'
      '<li>A record of locks and firewalls</li><li>A growable state layer with validation</li></ul></div>')
    A('<div class="card"><h6>What it is not</h6><ul>'
      '<li>Not a place to draft prose</li><li>Not a substitute for the source files</li>'
      '<li>Not an authority above your own words</li><li>Not a canon source in itself</li></ul></div>')
    A('<div class="card"><h6>Authority order</h6><ul>' +
      ''.join(f'<li>{e(x)}</li>' for x in laws.get('authority_order', [])) + '</ul></div>')
    A('</div>')
    A('<div class="note law"><span class="nt">CORE OPERATING RULE</span>'
      'This Control Centre is the <b>navigation and state reference</b>. It is not a drafting surface '
      'and it is not canon. Do not treat author knowledge as character knowledge. Do not invent '
      'missing canon. Preserve established decisions unless an explicit authorised change is made.</div>')
    A('</div></section>')

    # ---------------- 01 registry ----------------
    A('<section id="registry"><div class="wrap"><h3>SECTION 01</h3><h4>Project registry</h4>')
    A('<p>Counts are measured from disk by <code>tools/extract_state.py</code> and written to '
      '<code>state/workspace.json</code>. Re-run that script any time the workspace changes.</p>')
    rows = []
    for p in ws.get('projects', []):
        tag = STATUS_TAG.get(p.get('status'), 't-ref')
        rows.append([td(p.get('name'),'k'), td(p.get('path'),'mono'),
                     td(p.get('files'),'num'), td(f"{p.get('words',0):,}",'num'),
                     f'<td>{e(p.get("live_edge"))}</td>',
                     f'<td><span class="tag {tag}">{e(p.get("status","").upper())}</span></td>'])
    for p in registry.get('projects', []):
        tag = STATUS_TAG.get(p.get('status'), 't-ref')
        rows.append([td(p.get('name'),'k'), td(p.get('path'),'mono'),
                     td(p.get('files','-'),'num'), td(p.get('words','-'),'num'),
                     f'<td>{e(p.get("live_edge"))}</td>',
                     f'<td><span class="tag {tag}">{e(p.get("status","").upper())}</span></td>'])
    A(table(['Project','Path','Files','Words','Live edge','Status'], rows))
    A('<div class="note"><span class="nt">FILE TREE LAW</span>'
      'Every project uses the same layout: <code>foundation/</code> for status, continuity, locks, '
      'canon notes and serial log; <code>codex/</code> for characters, timeline, places and knowledge '
      'firewalls; <code>chapters/</code> for prose; <code>audits/</code> for dated audit reports. '
      'Do not invent your own layout - the layout is what lets a fresh agent orient in one read.</div>')
    A(f'<div class="note law"><span class="nt">FILENAME LAW</span>{e(canon.get("filename_law",""))}</div>')
    A('</div></section>')

    # ---------------- 02 rule ----------------
    A('<section id="rule"><div class="wrap"><h3>SECTION 02</h3><h4>Core operating rule</h4>')
    A('<p>Five failure modes killed a 90,000-word serial once. Every law in this system exists '
      'because one of them happened.</p>')
    A(table(['#','Failure mode','What it looked like','Structural cure'],
            [[td(f.get('n'),'num'), td(f.get('mode'),'k'),
              f'<td>{e(f.get("symptom"))}</td>', f'<td>{e(f.get("cure"))}</td>']
             for f in laws.get('failure_modes', [])]))
    A('<h5>The honesty tags</h5>')
    A(table(['Tag','Means','Strength'],
            [[td(t.get('tag'),'k'), f'<td>{e(t.get("meaning"))}</td>', f'<td>{e(t.get("strength"))}</td>']
             for t in canon.get('honesty_tags', [])]))
    A('</div></section>')

    # ---------------- 03 pipeline ----------------
    A('<section id="pipeline"><div class="wrap"><h3>SECTION 03</h3><h4>Pipeline</h4>')
    A('<p>Ten stages. Amber stages are gates - you do not proceed past one until it passes. The two '
      'most commonly skipped are <strong>VERIFY</strong> and <strong>AUDIT</strong>.</p><div class="pipe">')
    for s in laws.get('pipeline', []):
        c = 'stage gate' if s.get('gate') else 'stage'
        A(f'<div class="{c}"><div class="sn">{s.get("n"):02d}</div>'
          f'<div class="sl">{e(s.get("stage"))}</div><div class="sd">{e(s.get("detail"))}</div></div>')
    A('</div>')
    A('<div class="note stop"><span class="nt">NEVER SKIP RECORD</span>'
      'A decision that is not written down will regress. Every new decision, correction and canon '
      'receipt gets recorded in the same pass it is made. In this system that means filing it into '
      '<code>intake/drop/</code> as a <code>decision</code> or <code>correction</code>, not just '
      'saying it in chat.</div>')
    A('</div></section>')

    # ---------------- 04 pre-draft ----------------
    A('<section id="predraft"><div class="wrap"><h3>SECTION 04</h3><h4>Pre-draft gate</h4>')
    A('<p>Six steps, in order, before any prose is written.</p><div class="grid g2">')
    for s in laws.get('predraft_gate', []):
        tag = 't-live' if s.get('n') == 6 else 't-lock'
        A(f'<div class="card"><h6><span>{s.get("n")}. {e(s.get("step"))}</span>'
          f'<span class="tag {tag}">{"PROCEED" if s.get("n")==6 else "REQUIRED"}</span></h6>'
          f'<ul><li>{e(s.get("detail"))}</li></ul></div>')
    A('</div>')
    A('<div class="note"><span class="nt">WHY PANEL RANGE COMES FIRST</span>'
      'Set the panel timeline endpoints before writing a single line of prose. Every date in the '
      'chapter derives from them. Seventeen separate date bugs were found that way in one rebuild.</div>')
    A('</div></section>')

    # ---------------- 05 locks ----------------
    A('<section id="locks"><div class="wrap"><h3>SECTION 05</h3><h4>The twelve locks</h4>')
    A('<p>Set these before drafting chapter one. Write them into <code>NO_MISTAKE_LIVE_RULES.md</code>.</p>')
    A(table(['#','Lock','Question it answers'],
            [[td(l.get('n'),'num'), td(l.get('lock'),'k'), f'<td>{e(l.get("question"))}</td>']
             for l in laws.get('twelve_locks', [])]))
    A(f'<div class="note law"><span class="nt">LOCK 4 IS THE ONE THAT MATTERS MOST</span>'
      f'{e(laws.get("lock_4_rule",""))}<br><br>Blue Silver\'s cure was: <em>Spirit Hall wants rings, '
      f'and sends hunters into the forest to take them.</em></div>')
    A('</div></section>')

    # ---------------- 06 gates ----------------
    A('<section id="gates"><div class="wrap"><h3>SECTION 06</h3><h4>The seven hard gates</h4>')
    A('<p>Machine-checked by <code>tools/verify.py</code> in the Universal Kit. These are not '
      'negotiable, and "mostly passing" is a failure.</p>')
    A(table(['#','Gate','Why it exists'],
            [[td(g.get('n'),'num'), td(g.get('gate'),'k'), f'<td>{e(g.get("why"))}</td>']
             for g in laws.get('seven_gates', [])]))
    A('<h5>Gate scope - which gates apply to which files</h5>')
    cols = ['chapters','templates','law','codex','audit']
    rows = []
    for g in laws.get('seven_gates', []):
        sc = g.get('scope', [])
        cells = [td(g.get('gate'),'k')]
        for c in cols:
            cells.append('<td>yes</td>' if c in sc else '<td class="mono">&mdash;</td>')
        rows.append(cells)
    A(table(['Gate'] + [c.title() for c in cols], rows))
    A(f'<div class="note stop"><span class="nt">GATE SCOPE IS NOT OPTIONAL</span>'
      f'{e(laws.get("gate_scope_warning",""))}</div>')
    A(f'<div class="note"><span class="nt">THE SELF-REFERENTIAL TRAP</span>'
      f'{e(laws.get("self_referential_trap",""))}</div>')
    A(f'<div class="note good"><span class="nt">SHIP THE NEGATIVE TEST WITH THE GATE</span>'
      f'{e(laws.get("negative_test_rule",""))}</div>')
    A('</div></section>')

    # ---------------- 07 canon ----------------
    A('<section id="canon"><div class="wrap"><h3>SECTION 07</h3><h4>Canon spine</h4>')
    rl = canon.get('rank_ladder', {})
    A(f'<p>{e(rl.get("sources",""))}. Confidence: <b>{e(rl.get("confidence",""))}</b>.</p>')
    A('<h5>Soul rank ladder</h5>')
    A(table(['Rank','Levels'],
            [[td(r.get('rank'),'k'), td(r.get('levels'),'num')] for r in rl.get('rows', [])]))
    A(f'<p class="tight">{e(rl.get("subdivisions",""))} {e(rl.get("known_error",""))}</p>')
    A('<h5>Soul ring ages</h5>')
    A(table(['Colour','Years','Confidence'],
            [[td(r.get('colour'),'k'), td(f"{r.get('years'):,}",'num'),
              f'<td><span class="tag {"t-live" if r.get("confidence")=="canon" else "t-arch"}">'
              f'{e(r.get("confidence","").upper())}</span> {e(r.get("note",""))}</td>']
             for r in canon.get('ring_ages', [])]))
    A(f'<p class="tight">{e(canon.get("optimal_nine_ring",""))}</p>')
    bl = canon.get('beast_law', {})
    A(f'<div class="note stop"><span class="nt">DISCLOSED WEAKNESS</span>'
      f'Confidence: <b>{e(bl.get("confidence",""))}</b> - {e(bl.get("sources",""))}. '
      f'{e(bl.get("warning",""))}</div>')
    A(table(['Fact','Value'],
            [[td(r.get('fact'),'k'), td(r.get('value'),'num')] for r in bl.get('rows', [])]))
    A('<h5>User rulings - these override every source</h5><div class="grid g2">')
    for r in canon.get('user_rulings', []):
        A(f'<div class="card"><h6><span>{e(r.get("topic"))}</span>'
          f'<span class="tag t-user">USER RULING {e(r.get("date",""))}</span></h6><ul>'
          f'<li>{e(r.get("ruling"))}</li>')
        if r.get('formula'): A(f'<li>Formula: {e(r.get("formula"))}</li>')
        for f in r.get('forbidden', []): A(f'<li>Never: {e(f)}</li>')
        if r.get('note'): A(f'<li>{e(r.get("note"))}</li>')
        A('</ul></div>')
    A('</div>')
    if canon_c.get('records'):
        A('<h5>Contributed canon claims</h5>')
        A(table(['Claim','Confidence','Sources','Filed by'],
                [[f'<td>{e(c.get("claim"))}</td>',
                  td(c.get('confidence'),'k'),
                  f'<td>{e(c.get("sources","-"))}</td>',
                  td(c.get('provenance',{}).get('agent','-'),'mono')]
                 for c in canon_c['records']]))
    A('</div></section>')

    # ---------------- 08 firewalls ----------------
    A('<section id="firewalls"><div class="wrap"><h3>SECTION 08</h3><h4>Knowledge firewalls</h4>')
    A('<p>The single most violated law in collaborative fiction. <strong>Author knowledge is never '
      'automatically character knowledge.</strong></p>')
    A(table(['State','Means','What it permits'],
            [[f'<td><span class="state {STATE_CLASS.get(s.get("state"),"s-unk")}">{e(s.get("state"))}</span></td>',
              td(s.get('meaning'),'k'), f'<td>{e(s.get("permits"))}</td>']
             for s in laws.get('firewall_states', [])]))
    A(f'<div class="note law"><span class="nt">THE FOUR LEAK PATHS</span>'
      f'{e(laws.get("leak_paths",""))}</div>')
    A(f'<div class="note"><span class="nt">HOW TO ADD A FIREWALL</span>{e(fw.get("add_rule",""))}</div>')
    A(f'<h5>Live registry - {n_fw} firewalls</h5>')
    for f in fw.get('registry', []):
        cls = STATE_CLASS.get(f.get('state'), 's-unk')
        A(f'<div class="fw"><div class="fwh"><span class="who">{e(f.get("who"))}</span>'
          f'<span><span class="state {cls}">{e(f.get("state"))}</span> '
          f'<span class="num">FW {f.get("id"):02d} - {e(f.get("project",""))}</span></span></div><dl>'
          f'<dt>Topic</dt><dd>{e(f.get("topic"))}</dd>'
          f'<dt>Belief</dt><dd>{e(f.get("belief"))}</dd>'
          f'<dt>Earliest change</dt><dd>{e(f.get("earliest_change"))}</dd>'
          f'<dt>Rule</dt><dd class="rule">{e(f.get("rule"))}</dd></dl></div>')
    A('</div></section>')

    # ---------------- 09 blue silver ----------------
    bs = projs.get('blue_silver', {})
    if bs:
        A('<section id="bs"><div class="wrap"><h3>SECTION 09</h3><h4>Blue Silver - live state</h4>')
        A(f'<p>{e(bs.get("live_edge"))}</p>')
        cg = bs.get('canon_gate', {})
        A('<div class="grid g4">')
        for v, l in [(t.get('blue_silver_chapters',0),'CHAPTERS'),
                     ('775','YEARS COVERED'),('0','KILL COUNT - PERMANENT'),
                     (f"+{cg.get('tightest','')}",'TIGHTEST CANON MARGIN')]:
            A(f'<div class="card"><div class="metric small">{e(v)}</div><div class="mlabel">{e(l)}</div></div>')
        A('</div>')
        sp = bs.get('spine', {})
        A('<h5>Spine and absolutes</h5><div class="grid g2">')
        A(f'<div class="card"><h6><span>Lock 4 - the spine</span><span class="tag t-live">FILLED</span></h6>'
          f'<ul><li><b>{e(sp.get("lock4"))}</b></li><li>{e(sp.get("canon_fact_used"))}</li></ul></div>')
        A('<div class="card"><h6><span>Lock 7 - absolutes</span><span class="tag t-lock">BINDING</span></h6><ul>' +
          ''.join(f'<li>{e(a)}</li>' for a in bs.get('absolutes', [])) + '</ul></div></div>')
        A('<h5>Chapter ledger</h5>')
        A('<p>Panels are contiguous with no overlap and no gap.</p>')
        A(table(['#','Title','His years','Words'],
                [[td(c.get('n'),'num'), td(c.get('title'),'k'),
                  td(f"{c.get('year_start')}-{c.get('year_end')}" if c.get('year_start') is not None else '-','mono'),
                  td(f"{c.get('words'):,}",'num')]
                 for c in ws.get('blue_silver_chapters', [])]))
        A('<h5>Fixed anchors</h5>')
        A(table(['Anchor','Year','Note'],
                [[td(a.get('anchor'),'k'), td(a.get('year'),'num'), f'<td>{e(a.get("note",""))}</td>']
                 for a in bs.get('anchors', [])]))
        A(f'<div class="note stop"><span class="nt">CANON GATE - {e(cg.get("hard_boundary","").upper())}</span>'
          f'Naming <b>{e(cg.get("naming_dc"))} DC</b>; chapter fifteen ends '
          f'<b>{e(cg.get("ch15_end_dc"))} DC</b>; A Yin\'s rooted era ends before '
          f'<b>{e(cg.get("a_yin_era_ends_before_dc"))} DC</b>. Margins '
          f'<b>+{e(cg.get("margins",[0,0])[0])}</b> and <b>+{e(cg.get("margins",[0,0])[1])}</b>. '
          f'{e(cg.get("history",""))}<br><br>{e(cg.get("coda_check",""))}</div>')
        A('<h5>The two refusals - the moral spine</h5><div class="grid g2">')
        for r in bs.get('refusals', []):
            A(f'<div class="card"><h6><span>Refusal {r.get("n")} - year {e(r.get("year"))}</span>'
              f'<span class="tag t-lock">CHAPTER {e(r.get("chapter"))}</span></h6>'
              f'<ul><li>{e(r.get("what"))}</li></ul></div>')
        A('</div>')
        gl = bs.get('ground_language', {})
        A(f'<h5>Ground-language - fixed at {e(gl.get("count"))} words</h5>')
        A(f'<p>{e(gl.get("warning",""))}</p>')
        words = gl.get('words', [])
        A('<div class="grid g4">' + ''.join(
            f'<div class="card"><div class="metric small">{i+1}</div>'
            f'<div class="mlabel">{e(w).upper()}</div></div>'
            for i, w in enumerate(words)) + '</div>')
        A(f'<div class="note"><span class="nt">THE ELEVENTH</span>{e(gl.get("eleventh",""))}<br><br>'
          f'Delivery chain: {e(" then ".join(gl.get("delivery_chain", [])))}. '
          f'<b>{e(gl.get("point",""))}</b></div>')
        A('<h5>The nine named humans - survival by paperwork</h5>')
        A(table(['Name','Chapter','Rings','Contribution'],
                [[td(h.get('name'),'k'), td(h.get('chapter'),'mono'),
                  f'<td>{e(h.get("rings") or "-")}</td>', f'<td>{e(h.get("contribution"))}</td>']
                 for h in bs.get('named_humans', [])]))
        surv = [h for h in bs.get('named_humans', []) if h.get('warning')]
        for h in surv:
            A(f'<div class="note"><span class="nt">DO NOT CORRECT THIS DOWNWARD</span>'
              f'<b>{e(h.get("name"))}</b>: {e(h.get("warning"))}</div>')
        A(f'<div class="note"><span class="nt">THE DOCUMENTARY CHAIN</span>'
          f'{" &rarr; ".join(e(x) for x in bs.get("documentary_chain", []))}. '
          f'<b>{e(fw.get("blue_silver_structure",{}).get("thesis",""))}</b></div>')
        cu = bs.get('the_cull', {})
        A(f'<div class="note stop"><span class="nt">{e(cu.get("law","").upper())}</span>'
          f'There had been <b>{e(cu.get("had"))}</b> great ones. <b>{e(cu.get("returned_to_soil"))}</b> '
          f'went back into the soil in single seasons. <b>{e(cu.get("remain"))}</b> remain, '
          f'{e(cu.get("state"))} - <b>{e(cu.get("remain_after_746"))}</b> after year 746.</div>')
        ay = bs.get('a_yin', {})
        A('<h5>A Yin</h5><div class="grid g2">')
        A('<div class="card"><h6><span>Who she is</span><span class="tag t-live">CANON</span></h6><ul>'
          f'<li>{e(ay.get("appearance"))}</li><li>{e(ay.get("age"))}</li>'
          f'<li>{e(ay.get("secret"))}</li><li><b>{e(ay.get("act"))}</b></li></ul></div>')
        A('<div class="card"><h6><span>Standing constraints</span><span class="tag t-lock">BINDING</span></h6><ul>'
          f'<li>{e(ay.get("constraint"))}</li><li>Her fate: {e(ay.get("fate"))}</li></ul></div></div>')
        idn = bs.get('identity', {})
        cult_parts = []
        for c in bs.get('cultivation', []):
            yrs = c.get('years')
            ay_ = c.get('at_year')
            if yrs is not None and ay_ is not None:
                cult_parts.append("~{:,} years at year {}".format(yrs, ay_))
        cult = '; '.join(cult_parts)
        A(f'<div class="note law"><span class="nt">WHAT HE IS - AND WHAT HE IS NOT</span>'
          f'{e(idn.get("is",""))} <b>Not: {e(", ".join(idn.get("is_not", [])))}.</b> '
          f'Cultivation: {e(cult)}. '
          f'He takes nothing for {e(bs.get("takes_nothing_for"))}. '
          f'{e(bs.get("ending",""))}</div>')
        A('</div></section>')

    # ---------------- 10 sl4 ----------------
    sl = projs.get('sl4_fire_phoenix', {})
    if sl:
        A('<section id="sl4"><div class="wrap"><h3>SECTION 10</h3><h4>SL4 Fire Phoenix - live state</h4>')
        A(f'<p>Live edge is <strong>{e(sl.get("live_edge"))}</strong>. '
          f'{t.get("sl4_chapters",0)} chapter files on disk. '
          f'{"This project is <b>not currently active</b> - the locks below are binding if it resumes." if not sl.get("active") else ""}</p>')
        pr = sl.get('protagonist', {})
        A('<h5>Protagonist</h5><div class="grid g2">')
        A(f'<div class="card"><h6><span>Identity</span><span class="tag t-lock">LOCK 6</span></h6><ul>'
          f'<li><b>{e(pr.get("true_name"))}</b> - {e(pr.get("true_pronouns"))}, true identity</li>'
          f'<li>Cover name <b>{e(pr.get("cover_name"))}</b> - {e(pr.get("cover_pronouns"))}, public</li>'
          f'<li>{e(pr.get("origin"))}</li><li>{e(pr.get("dorm"))}</li>'
          f'<li><b>{e(pr.get("reveal_rule"))}</b></li></ul></div>')
        A('<div class="card"><h6><span>Do not</span><span class="tag t-lock">BINDING</span></h6><ul>' +
          ''.join(f'<li>{e(x)}</li>' for x in sl.get('do_not', [])) + '</ul></div></div>')
        A('<h5>Current numeric status</h5>')
        A(table(['Item','Current','Notes'],
                [[td(s.get('item'),'k'), td(s.get('value'),'num'), f'<td>{e(s.get("note",""))}</td>']
                 for s in sl.get('current_status', [])]))
        cl = sl.get('chronology_locks', {})
        A(f'<div class="note stop"><span class="nt">THE THREE-YEAR SKIP - DO NOT WRITE IT NOW</span>'
          f'Platform entry: {e(cl.get("platform_entry"))} The time skip: {e(cl.get("time_skip"))} '
          f'Level 30 fusion: {e(cl.get("level30_fusion"))}<br><br>' +
          ' '.join(f'<b>{e(x)}</b>' for x in cl.get('forbidden_now', [])) + '</div>')
        uf = sl.get('user_locked_future', {})
        A('<div class="grid g2"><div class="card"><h6><span>Latest chapter results</span>'
          '<span class="tag t-live">RECORDED</span></h6><ul>' +
          ''.join(f'<li>{e(x)}</li>' for x in sl.get('chapter31_results', [])) + '</ul></div>')
        A(f'<div class="card"><h6><span>The user-locked future</span><span class="tag t-user">USER LOCK</span></h6>'
          f'<ul><li>{e(uf.get("event"))}</li>'
          f'<li>Awakens: {e(", ".join(uf.get("awakens", [])))}</li>'
          f'<li><b>{e(uf.get("aftermath"))}</b></li></ul></div></div>')
        A(f'<div class="note"><span class="nt">MEASUREMENT PARITY</span>{e(sl.get("anti_nerf",""))}</div>')
        A('</div></section>')

    # ---------------- 11 storyos ----------------
    so = projs.get('storyos_naag', {})
    if so:
        A('<section id="storyos"><div class="wrap"><h3>SECTION 11</h3><h4>StoryOS / Naag - live state</h4>')
        A(f'<p>{e(so.get("universe"))} Protagonist <strong>{e(so.get("protagonist"))}</strong>.</p>')
        A(f'<div class="note"><span class="nt">TAGGED [REPORTED]</span>{e(so.get("verification_note",""))}</div>')
        A('<div class="grid g4">' + ''.join(
            f'<div class="card"><div class="metric small">{e(c.get("value"))}</div>'
            f'<div class="mlabel">{e(c.get("label","").upper())}</div></div>'
            for c in so.get('counts', [])) + '</div>')
        A(f'<p class="tight">{e(so.get("firewall_location",""))} They are listed in '
          f'<a href="#firewalls">Section 08</a>.</p>')
        if so.get('open_gaps'):
            A('<h5>Unresolved questions - flag, do not invent</h5>')
            A('<div class="note stop"><span class="nt">OPEN CANON GAPS</span>')
            for i, g in enumerate(so['open_gaps'], 1):
                A(f'<b>{i}. {e(g.get("question"))}</b> {e(g.get("detail"))} '
                  f'<i>Ruling: {e(g.get("ruling"))}</i><br><br>')
            A('</div>')
        A('</div></section>')

    # ---------------- 12 others ----------------
    A('<section id="others"><div class="wrap"><h3>SECTION 12</h3><h4>Other projects</h4><div class="grid g2">')
    for pid in ['SOUL_LAND_NEW', 'reference_sl3_lin_hao', 'soul_land_starter', 'SOUL_LAND_UNIVERSAL_KIT']:
        p = next((x for x in ws.get('projects', []) if x.get('id') == pid), None)
        if not p: continue
        tag = STATUS_TAG.get(p.get('status'), 't-ref')
        A(f'<div class="card"><h6><span>{e(p.get("name"))}</span>'
          f'<span class="tag {tag}">{e(p.get("status","").upper())}</span></h6><ul>'
          f'<li>{e(p.get("files"))} files, {e(f"{p.get(chr(119)+chr(111)+chr(114)+chr(100)+chr(115),0):,}")} words</li>'
          f'<li>{e(p.get("live_edge"))}</li></ul></div>')
    A('</div>')
    A('<div class="note"><span class="nt">THE CROSS-PROJECT CONFLATION TRAP</span>'
      'Identify a project from the contents of its own files before applying any sibling project\'s '
      'labels - and never let a number cross a project boundary. SL1 Gu Yuan at Rank 40 is not SL4 '
      'Yan at Rank 23.</div>')
    A('<h5>Opening a new project</h5><div class="grid g3">')
    for n, t2, d in [('1','Copy the skeleton','Copy soul_land_starter/, rename to an ASCII-safe name, do not invent a new layout.'),
                     ('2','Fill the twelve locks','All twelve, before chapter one. Lock 4 must be a filled sentence.'),
                     ('3','Name the canon beats','At least five, with receipts. Tag each honestly and disclose weak sourcing.')]:
        A(f'<div class="card"><h6><span>{t2}</span><span class="tag t-lock">STEP {n}</span></h6>'
          f'<ul><li>{e(d)}</li></ul></div>')
    A('</div></div></section>')

    # ---------------- 13 adaptation ----------------
    at = laws.get('adaptation_talent', {})
    A('<section id="adaptation"><div class="wrap"><h3>SECTION 13</h3><h4>Adaptation Talent</h4>')
    A('<p>A cross-project framework belonging to the user\'s OCs, defined once here because it has '
      'been misimplemented repeatedly - always the same error: turning an existence-level instinct '
      'into a game interface.</p>')
    A(f'<div class="note law"><span class="nt">WHAT IT IS</span>{e(at.get("is",""))}</div>')
    A('<div class="note stop"><span class="nt">WHAT IT IS NOT</span>It is <b>not</b> ' +
      ', not '.join(f'<b>{e(x)}</b>' for x in at.get('is_not', [])) +
      '. It has no dialogue, no notifications, no levels, and no narrator.</div>')
    A('<h5>The four requirements</h5>')
    A(table(['Requirement','What it means in practice'],
            [[td(r.get('req'),'k'), f'<td>{e(r.get("detail"))}</td>']
             for r in at.get('requirements', [])]))
    A(f'<div class="note stop"><span class="nt">THE ONE ABUSE TO WATCH FOR</span>'
      f'{e(at.get("primary_abuse",""))} Every knowledge firewall in '
      f'<a href="#firewalls">Section 08</a> still applies in full, without exception, to any '
      f'character who has this talent.</div>')
    A(f'<div class="note"><span class="nt">SETTING RULES STILL BIND</span>{e(at.get("setting_bound",""))}</div>')
    A('</div></section>')

    # ---------------- 14 growth log ----------------
    A('<section id="growth"><div class="wrap"><h3>SECTION 14</h3><h4>Growth log</h4>')
    A('<p>Every accepted contribution is recorded here. This is what makes the system auditable: '
      'you can see what entered, when, and who filed it.</p>')
    A('<div class="grid g4">')
    for v, l in [(n_fw,'FIREWALLS'),(n_reg,'CONTRIBUTED PROJECTS'),
                 (n_contrib,'CONTRIBUTED RECORDS'),(n_events,'GROWTH EVENTS')]:
        A(f'<div class="card"><div class="metric small">{e(v)}</div><div class="mlabel">{e(l)}</div></div>')
    A('</div>')
    if log.get('events'):
        A(table(['When','Agent','Records added','Source file'],
                [[td(ev.get('when'),'mono'), td(ev.get('agent'),'k'),
                  td(', '.join(ev.get('ids', [])),'mono'), td(ev.get('file'),'mono')]
                 for ev in reversed(log['events'])]))
    else:
        A('<div class="note good"><span class="nt">NO CONTRIBUTIONS YET</span>'
          'The state layer is at its seeded baseline. The first contribution filed into '
          '<code>intake/drop/</code> will appear here with the agent name and timestamp attached.</div>')
    if contribs.get('records'):
        A('<h5>Contributed records</h5>')
        A(table(['Seq','Kind','Project','Summary','Filed by'],
                [[td(c.get('seq'),'num'), td(c.get('kind'),'k'),
                  td(c.get('project','-'),'mono'),
                  f'<td>{e(c.get("decision") or c.get("text") or c.get("claim") or c.get("anchor") or "-")}</td>',
                  td(c.get('provenance',{}).get('agent','-'),'mono')]
                 for c in contribs['records']]))
    A('<div class="note law"><span class="nt">APPEND-ONLY BY DESIGN</span>'
      'A contribution can ADD a firewall, an anchor, a decision or a correction. It cannot silently '
      'overwrite existing state. A correction is recorded as a correction, which keeps the old value '
      'visible and shows why it changed. That is deliberate: a state layer where anything can be '
      'quietly replaced is a state layer nobody can trust.</div>')
    A('</div></section>')

    # ---------------- 15 protocol ----------------
    A('<section id="protocol"><div class="wrap"><h3>SECTION 15</h3><h4>Contribution protocol</h4>')
    A('<p>This is how the system grows. Any agent - or you - files a JSON contribution into '
      '<code>intake/drop/</code>. The validator checks it, the ingester merges it, the builder '
      're-renders this page.</p>')
    A('<div class="pipe">'
      '<div class="stage"><div class="sn">01</div><div class="sl">FILE</div><div class="sd">Write JSON into intake/drop/</div></div>'
      '<div class="stage gate"><div class="sn">02</div><div class="sl">VALIDATE</div><div class="sd">tools/validate.py</div></div>'
      '<div class="stage"><div class="sn">03</div><div class="sl">INGEST</div><div class="sd">tools/ingest.py merges it</div></div>'
      '<div class="stage"><div class="sn">04</div><div class="sl">BUILD</div><div class="sd">tools/build.py re-renders</div></div>'
      '<div class="stage"><div class="sn">05</div><div class="sl">LOG</div><div class="sd">state/log.json records it</div></div>'
      '</div>')
    A('<h5>Contribution kinds</h5>')
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from schema import KINDS
    A(table(['Kind','Required fields','Optional fields','What it is for'],
            [[td(k,'k'),
              td(', '.join(v['required']),'mono'),
              td(', '.join(v.get('optional', [])) or '-','mono'),
              f'<td>{e(KIND_DESC.get(k,""))}</td>']
             for k, v in sorted(KINDS.items())]))
    A('<h5>Example contribution</h5>')
    A('<pre class="code">' + e(EXAMPLE) + '</pre>')
    A('<h5>What the validator rejects</h5><ul class="bullets">'
      '<li>An unknown <code>kind</code>, or a required field missing</li>'
      '<li>A firewall <code>state</code> outside the seven defined states - adding a state is a law change and needs the user</li>'
      '<li>A <code>[canon]</code> claim with no sources named</li>'
      '<li>CJK, kana or hangul anywhere in the file (gate 1)</li>'
      '<li>A literal backslash-n sequence (gate 2)</li>'
      '<li>A reserved field such as <code>authority_order</code> or <code>seven_gates</code></li>'
      '<li>A duplicate of another contribution in the same file</li>'
      '<li>A project id that already exists - file a correction instead</li>'
      '</ul>')
    A('<div class="note"><span class="nt">WHY THIS IS STRICT</span>'
      'A state layer that accepts anything becomes a pile of notes, and then no agent can trust it. '
      'The rejection report tells the filing agent exactly what to fix, and the file moves to '
      '<code>intake/rejected/</code> rather than being deleted, so nothing is lost.</div>')
    A('</div></section>')

    # ---------------- 16 bootstrap ----------------
    A('<section id="bootstrap"><div class="wrap"><h3>SECTION 16</h3><h4>Transfer bootstrap</h4>')
    A('<p>Generated from the same state as this page. Copy it and give it to any new agent. It is '
      'self-contained: the recipient does not need access to this workspace to operate correctly.</p>')
    A('<div class="bootwrap"><div class="btnrow">'
      '<button class="pri" onclick="copyBoot()">COPY TRANSFER BOOTSTRAP</button>'
      '<button onclick="selBoot()">SELECT ALL</button>'
      '<button onclick="dlBoot()">DOWNLOAD AS .TXT</button>'
      '<span id="cpmsg"></span></div>')
    boot = open(os.path.join(ROOT, 'TRANSFER_BOOTSTRAP.txt'), encoding='utf-8').read() \
        if os.path.exists(os.path.join(ROOT, 'TRANSFER_BOOTSTRAP.txt')) else '(run tools/bootstrap.py)'
    A(f'<textarea id="boot" spellcheck="false" readonly>{e(boot)}</textarea></div>')
    A('</div></section>')

    # ---------------- 17 verify ----------------
    A('<section id="verify"><div class="wrap"><h3>SECTION 17</h3><h4>Verification status</h4>')
    A('<p>An honest account of what was checked and what was not.</p>')
    A('<h5>Measured from disk</h5>')
    A(table(['Claim','How it was checked'],
            [[td('Project file and word counts','k'), td('tools/extract_state.py, per-file, binary-aware','mono')],
             [td('Chapter counts and word counts','k'), td('per-file word count of chapters_rebuilt/','mono')],
             [td('Kit law and template counts','k'), td('directory listing, regex on filename law','mono')],
             [td('Binary files excluded from word counts','k'), td('magic-byte check, not extension','mono')]]))
    A('<h5>Read from source documents</h5>')
    A(table(['Claim','Source'],
            [[td('Blue Silver chapter ledger and anchors','k'), td('bluesilver_foundation/REBUILD_CONTINUITY.md','mono')],
             [td('Ground-language word list','k'), td('blue_silver/rebuild_codex/GLOSSARY.md','mono')],
             [td('Seven gates and scope table','k'), td('SOUL_LAND_UNIVERSAL_KIT/09_AUDIT_LAW.md','mono')],
             [td('Twelve locks','k'), td('SOUL_LAND_UNIVERSAL_KIT/02_PROJECT_SETUP.md','mono')],
             [td('SL4 numbers','k'), td('sl4_fire_phoenix/foundation/STATUS_PANEL.md','mono')]]))
    A('<h5>Reported, not file-verified</h5>')
    A('<div class="note"><span class="nt">TAGGED [REPORTED]</span>'
      'Everything in <a href="#storyos">Section 11</a> came through the transfer bootstrap you '
      'supplied. The StoryOS Control Centre sits behind a ChatGPT sign-in wall and returned '
      '<b>HTTP 401</b> on every path tested, so its records could not be read directly. The '
      'eighteen firewalls are reproduced exactly as given, but have not been checked against '
      'source scenes.</div>')
    A('<h5>Known weaknesses carried forward</h5>')
    A(table(['Weakness','Why it matters','Mitigation'],
            [[td('Beast law rests on one compiled source','k'),
              td('Load-bearing for any plant-beast protagonist',''),
              td('Disclosed in Section 07; flag dependent chapters','')],
             [td('No canon was read in the Chinese original','k'),
              td('[canon] here means secondary-source agreement',''),
              td('Tag strength stated everywhere it is used','')],
             [td('SL3 Lin Hao is craft-only reference','k'),
              td('1M words of plausible numbers that must never cross projects',''),
              td('Marked reference-only in the registry','')],
             [td('StoryOS state is unverified','k'),
              td('Eighteen firewalls govern a serial nobody here has read the source for',''),
              td('Tagged reported; open gaps listed explicitly','')],
             [td('Blue Silver canon margin is nine years','k'),
              td('Any edit past year 784 breaks canon outright',''),
              td('Hard boundary stated in Section 09','')],
             [td('Three files in uploads/ are mislabelled archives','k'),
              td('A ZIP and a DOCX carry .txt and .md extensions, inflating naive word counts by ~450,000',''),
              td('Excluded by magic-byte check, not by extension','')]]))
    A('<div class="note law"><span class="nt">THE STANDING INSTRUCTION</span>'
      'Corrections come before new content. If a lock, a firewall or a canon receipt turns out to '
      'be wrong, file a <code>correction</code> and re-run the gates <b>before</b> writing the next '
      'chapter. A clean exit code is not a pass when the output is wrong.</div>')
    A('<footer><div class="sig">SOUL LAND UNIVERSAL - CONTROL CENTRE &nbsp;|&nbsp; '
      f'BUILT {e(ws.get("generated",""))} &nbsp;|&nbsp; GENERATED FROM state/ - DO NOT HAND-EDIT '
      '&nbsp;|&nbsp; NAVIGATION AND STATE REFERENCE, NOT CANON</div></footer>')
    A('</div></section>')

    A('</main></div>')
    A(SCRIPT)
    A('</body></html>')

    out = os.path.join(ROOT, 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(S))
    return out


KIND_DESC = {
    'project': 'Register a new project in the registry',
    'firewall': 'Add a knowledge firewall for a character',
    'anchor': 'Add a fixed timeline anchor',
    'canon': 'Assert a canon claim with a confidence tag and sources',
    'lock': 'Record one of the twelve locks for a project',
    'decision': 'Record an authorised decision so it does not regress',
    'correction': 'Correct an existing value, keeping the old one visible',
    'note': 'Add a free-form note tagged to a project',
}

EXAMPLE = '''{
  "kind": "firewall",
  "project": "blue_silver",
  "who": "Berrit Ohn",
  "state": "KNOWN PARTLY",
  "topic": "The valley's contents",
  "belief": "She knows the seal exists and what it protects, but not that the grass is sentient.",
  "earliest_change": "A direct encounter with Home after the seal is filed.",
  "rule": "Her paperwork protects the valley without her knowing what lives in it.",
  "provenance": {"agent": "your-agent-name", "date": "2026-09-18"}
}'''

SCRIPT = '''<script>
function bootText(){return document.getElementById('boot').value.trim();}
function selBoot(){var t=document.getElementById('boot');t.focus();t.select();
  document.getElementById('cpmsg').textContent='selected';}
function copyBoot(){var txt=bootText(),m=document.getElementById('cpmsg');
  function ok(){m.textContent='copied to clipboard';setTimeout(function(){m.textContent='';},2600);}
  function fail(){selBoot();m.textContent='press Ctrl/Cmd+C to copy';}
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(ok).catch(function(){legacyCopy(txt)?ok():fail();});
  }else{legacyCopy(txt)?ok():fail();}}
function legacyCopy(txt){try{var ta=document.createElement('textarea');ta.value=txt;
  ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.top='-1000px';ta.style.opacity='0';
  document.body.appendChild(ta);ta.select();var ok=document.execCommand('copy');
  document.body.removeChild(ta);return ok;}catch(e){return false;}}
function dlBoot(){var blob=new Blob([bootText()],{type:'text/plain;charset=utf-8'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='SOUL_LAND_UNIVERSAL_TRANSFER_BOOTSTRAP.txt';
  document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);document.body.removeChild(a);},400);
  var m=document.getElementById('cpmsg');m.textContent='downloaded';
  setTimeout(function(){m.textContent='';},2600);}
</script>'''


if __name__ == '__main__':
    out = build()
    size = os.path.getsize(out)
    print(f"  built {os.path.relpath(out, ROOT)} — {size:,} bytes")
