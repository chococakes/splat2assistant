import os, logging
from livereload import Server
from flask import Flask, render_template, render_template_string, request, url_for, redirect, session
from wtforms import Form, StringField
from wtforms.validators import InputRequired, ValidationError

import splatdata

app = Flask(__name__)
app.secret_key = os.urandom(32)

logger = logging.getLogger('splathelper')
logger.setLevel(logging.INFO)

# TODO: Make a 404 page if the page is accessed incorrectly
@app.route('/', methods=['GET', 'POST'])
def index():
    cookieform = IKSMForm()
    return render_template('index.html', form=cookieform)

@app.route('/viewer', methods=['POST'])
def viewer():
    form = IKSMForm(request.form)
    if form.validate():
        cookie = form.cookie.data
        return redirect(url_for('full_viewer', id=cookie))
    return redirect('/')

@app.route('/viewer/<id>')
def full_viewer(id):
    try:
        results, pid = splatdata.load_player_data(id)
        summary, _ = splatdata.summary(results)
        weapon_data = splatdata.weapon_summary(results)
        return render_template('viewer_home.html', cookie=id, results=results, summary=summary, weapons=weapon_data, player_id=pid)
    except KeyError:
        return render_template_string("<h2>Invalid request!</h2>")

@app.route('/viewer/<cookie>/<id>')
def indiv_viewer(cookie, id):
    try:
        result, enemies, allies = splatdata.create_result(cookie, id)
        return render_template('viewer_indiv.html', enemies=enemies, allies=allies, result=result)
    except KeyError:
        return render_template_string("<h2>Invalid request!</h2>")

class IKSMForm(Form):
    cookie = StringField('Enter in your IKSM session cookie or player ID.', [InputRequired()])

    def validate_cookie(form, field):
        if len(field.data) != 40 and len(field.data) != 16:
            raise ValidationError("Invalid cookie or ID.")
        try:
            splatdata.load_player_data(field.data)
        except KeyError:
            raise ValidationError('Invalid cookie.')
        except FileNotFoundError:
            raise ValidationError("That ID doesn't have any data on this server. Try entering in your iksm_session cookie instead.")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    #server = Server(app.wsgi_app)
    #server.serve()
