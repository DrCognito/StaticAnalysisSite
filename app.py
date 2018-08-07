from itertools import zip_longest
from json import load as json_load
from os import environ
from pathlib import Path
from urllib.parse import quote, unquote

from dotenv import load_dotenv
from flask import Flask, abort, render_template, url_for
from flask_frozen import Freezer

load_dotenv(dotenv_path="setup.env")
app = Flask(__name__)
freezer = Freezer(app)


def get_metadata_locations(path: Path) -> dict:
    output = {}
    metadata_paths = path.glob('**/meta_data.json')
    for p in metadata_paths:
        name = str(p.parent).split('\\')[-1]
        output[name] = p

    return output


metadata_dict = get_metadata_locations(Path(environ['PLOT_DIRECTORY']))


def render_team(team: str, dataset='default'):
    # Handles conversion of "%" notation from url strings to normal strings.
    team = unquote(team)
    if team not in metadata_dict:
        abort(404)

    def _side_dicts(data: dict, side: str) -> dict:
        output = {}
        # Drafts
        output["drafts_link"] = "#{}_drafts".format(side)
        output["plot_drafts"] = data["plot_{}_drafts".format(side)]
        # Wards
        output["wards_link"] = "#{}_wards".format(side)
        output["ward_t1"] = data["plot_ward_t1_{}".format(side)]
        output["ward_t2"] = data["plot_ward_t2_{}".format(side)]
        output["ward_t3"] = data["plot_ward_t3_{}".format(side)]

        # Positioning
        output["pos_link1"] = "#{}_pos1".format(side)
        output["pos_link2"] = "#{}_pos2".format(side)
        output["pos_link3"] = "#{}_pos3".format(side)
        output["pos_link4"] = "#{}_pos4".format(side)
        output["pos_link5"] = "#{}_pos5".format(side)

        output["p1pos"] = data.get("plot_pos_t1_{}".format(side))
        output["p2pos"] = data.get("plot_pos_t2_{}".format(side))
        output["p3pos"] = data.get("plot_pos_t3_{}".format(side))
        output["p4pos"] = data.get("plot_pos_t4_{}".format(side))
        output["p5pos"] = data.get("plot_pos_t5_{}".format(side))

        # Smoke
        output["smoke_link"] = "#{}_smoke".format(side)
        output["smoke"] = data["plot_smoke_{}".format(side)]

        # Scan
        output["scan_link"] = "#{}_scan".format(side)
        output["scan"] = data["plot_scan_{}".format(side)]

        return output

    with open(metadata_dict[team], 'r') as file:
        json_file = json_load(file)

        if dataset not in json_file:
            abort(404)

        data = json_file[dataset]
        replay_list = list(zip_longest(data['replays_dire'],
                                       data['replays_radiant']))
        dire_dict = _side_dicts(data, "dire")
        radiant_dict = _side_dicts(data, "radiant")

        return render_template('team.j2',
                               team=team,
                               replays=replay_list,
                               dire_dict=dire_dict,
                               radiant_dict=radiant_dict)


@app.route("/")
def index():
    return "Hello world!"


@app.route("/<string:team>/")
def team(team):
    return render_team(team)


@freezer.register_generator
def team():
    for p in metadata_dict.keys():
        yield {'team': p}


if __name__ == '__main__':
    app.run(port=8000)
