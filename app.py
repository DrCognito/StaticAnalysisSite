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


def url_path(path_in: str, endpoint='static'):
    path_in = path_in.replace("\\", "/")
    path_in = "plots/" + path_in
    return url_for(endpoint, filename=path_in)


def render_team(team: str, dataset='default'):
    # Handles conversion of "%" notation from url strings to normal strings.
    team = unquote(team)
    if team not in metadata_dict:
        abort(404)

    def _side_dicts(data: dict, side: str) -> dict:
        output = {}
        # Drafts
        output["drafts_link"] = "#{}_drafts".format(side)
        output["plot_drafts"] = url_path(data["plot_{}_drafts".format(side)])
        #output["plot_drafts"] = url_for('static', filename=data["plot_{}_drafts".format(side)])
        # # Wards
        uniq_wards = set(data['plot_ward_{}'.format(side)])
        output["ward_links"] = ["#{}_".format(side) + w for w in
                                data['plot_ward_names']]
        output["ward_title"] = data['plot_ward_names']
        output["ward_plots"] = ['plots/' + p.replace("\\", "/") for p in
                                uniq_wards]

        # Positioning
        output['pos_names'] = data['player_names']

        output['pos_plots'] = ['plots/' + p.replace("\\", "/") for p in
                               data['plot_pos_{}'.format(side)][:5]]

        # Smoke
        output["smoke_link"] = "#{}_smoke".format(side)
        output["smoke"] = url_path(data["plot_smoke_{}".format(side)])

        # Scan
        output["scan_link"] = "#{}_scan".format(side)
        output["scan"] = url_path(data["plot_scan_{}".format(side)])

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

        summary_dict = {}
        summary_dict['draft_summary'] = url_path(data["plot_draft_summary"])
        summary_dict['pair_picks'] = url_path(data["plot_pair_picks"])
        summary_dict['pick_context'] = url_path(data["plot_pick_context"])
        summary_dict['win_rate'] = url_path(data["plot_win_rate"])

        return render_template('team.j2',
                               team=team,
                               replays=replay_list,
                               dire_dict=dire_dict,
                               radiant_dict=radiant_dict,
                               summary=summary_dict)


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
