import plotly.graph_objects as go
import csv
import json
import re
import sys 

def as_number(s):
    if not s.strip():
        return 0 
    return int(s.replace(',',''))

with open('EUDublin.csv', encoding='utf-8-sig') as csvfile:
    candidate_results = list(csv.DictReader(csvfile))

rounds_count = len([k for k in candidate_results[0].keys() if re.compile("^c\\d+$").match(k)])

max_transferrals = 0
for round in range(1, rounds_count):
    round_label = f"{round} to {round + 1}"
    for r in candidate_results:
        transferrals = as_number(r[round_label])
        if transferrals > max_transferrals:
            max_transferrals = transferrals

transferral_opacity_coeff = 1 / max_transferrals 

per_round = {}

candidate_names = []
sankey_source = []
sankey_target = []
sankey_value = []
sankey_link_color = []
sankey_node_color = []
sankey_node_customdata = []

party_colors = {
    "FF": '#40b34f',
    "FG": '#2f3590',
    "SF": '#088560',
    "Green": '#b4d144',
    "Lab": '#c72831',
    "II": '#000000',
    "I4C": '#000000',
    "PBP-Sol": '#000000',
    "Aontú": '#000000',
    "Ind": '#000000',
    "IF": '#000000',
    "IFP": '#000000',
    "NP": '#000000',
    "TIP": '#000000',
    "SD": '#6600e6',
    "": '#000000',
}

def add_candidate_label(candidate):
    if candidate not in candidate_names:
        candidate_names.append(candidate)

sankey_per_node_data = {r['Candidate']: {"transferrals": [], "eliminated": None, "party": r['Party']} for r in candidate_results}

for _round in range(1, rounds_count):
    round_label = f"{_round} to {_round + 1}"
    try:
        round_loser = [c["Candidate"] for c in candidate_results if as_number(c[round_label]) < 0][0]
    except IndexError:
        round_loser = None

    sankey_per_node_data[round_loser]["eliminated"] = _round

    for r in candidate_results:
        candidate_name = r["Candidate"]
        transferrals = as_number(r[round_label])
        opacity = max(0.1, transferrals * transferral_opacity_coeff)
        if transferrals > 0:
            add_candidate_label(round_loser)
            add_candidate_label(candidate_name)

            sankey_source.append(candidate_names.index(round_loser))
            sankey_target.append(candidate_names.index(candidate_name))
            sankey_value.append(transferrals)
            sankey_link_color.append(f"rgba(100,200,255,{opacity})")
            sankey_node_color.append(party_colors[r['Party']])

            sankey_per_node_data[round_loser]["transferrals"].append((candidate_name, transferrals))

def generate_sankey(labels, source, target, value):

    for candidate_name in labels:
        hover = f"<b>{candidate_name} ({sankey_per_node_data[candidate_name]['party']})</b>"
        if sankey_per_node_data[candidate_name]["eliminated"]:
            hover += f"<br />Eliminated in count {sankey_per_node_data[candidate_name]['eliminated']}<br /><br />Transfers from this candidate:"
            for target_candidate, count in sorted(sankey_per_node_data[candidate_name]["transferrals"], key=lambda x: x[1], reverse=True):
                hover += f"<br />{count} --> {target_candidate}"
        sankey_node_customdata.append(hover)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = labels,
            color = ["#000000"] + sankey_node_color,
            customdata = sankey_node_customdata,
            hovertemplate = '%{customdata}'
        ),
        link = dict(
            source = source, # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = target,
            value = value,
            color = sankey_link_color
        )
    )])

    fig.update_layout(title_text="EU MEPs Election 2024 - Transferrals in Dublin", font_size=12)
    fig.show()

generate_sankey(candidate_names, sankey_source, sankey_target, sankey_value)