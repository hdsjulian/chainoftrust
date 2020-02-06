from flask import render_template, flash, redirect, url_for
from app import app 
from flask_login import current_user, login_user
from app.models import User, Artifact, Handover, Media, Text, MediaType
from app.forms import RegisterForm, UpdateForm
from app import db
@app.route('/')
@app.route('/index')
def index():
	return render_template('/index.html')
@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user_id = request.args.get('user_id')
    access_hash = request.args.get('access_hash')
    user = User.query.get(user_id)
    if user is None or user.access_hash != access_hash:
    	flash('Invalid user id and access hash combination')
    	return redirect(url_for('index'))
    login_user(user)
    return redirect(url_for('index'))
@app.route('/artifact/<artifact_id>')
@app.route('/artifact/<artifact_id>/<artifact_hash>')
def artifact(artifact_id, artifact_hash=0):
	artifact = Artifact.query.get(artifact_id)
	handover_count = Handover.query.join(Artifact).filter(Artifact.id==Handover.artifact_id).count()
	if artifact_id is not None and artifact.access_hash == artifact_hash:
		editable = True
	else: 
		editable = False

	return render_template('artifact.html', artifact_id = artifact_id,  access_hash=artifact_hash, handover_count=handover_count, editable=editable)


@app.route('/register/<artifact_id>/<artifact_hash>', methods=['GET','POST'])
def register(artifact_id, artifact_hash):
	artifact = Artifact.query.get(artifact_id)
	form = RegisterForm()
	if form.is_submitted():
		print ("submitted")
		print (form.email.data)
	if form.validate():
		print ("valid")
	else: 
		print(form.errors)
	if artifact_id is None or artifact.access_hash != artifact_hash:
		flash("invalid artifact id and access hash combination")
		return redirect(url_for('index'))
	if form.validate_on_submit():
		print("foobla")
		user = User.get_or_create_user(form.email.data, form.name.data)
		predecessor = Handover.query.join(Artifact).filter(Artifact.id==Handover.artifact_id).order_by(Handover.id.desc()).limit(1)
		if form.text.data != "":
			media = Media(type=MediaType.text)
			db.session.add(media)
			db.session.commit()
			text = Text(media_id = media.id, text = form.text.data)
			db.session.add(text)
			db.session.commit()
		handover = Handover(artifact_id=artifact_id,predecessor_id = predecessor[0].id, lat = form.lat.data, lon = form.lon.data, user_id = user.id)
		handover.media_id = media.id
		db.session.add(handover)
		db.session.commit()
		print (handover.id)
		return redirect(url_for('handover', handover_id = handover.id))
	else: 
		print("doesn't validate")
	handover_count = Handover.query.join(Artifact).filter(Artifact.id==Handover.artifact_id).count()
	return render_template('register.html',title = "Register Handover", form=form, artifact_id = artifact_id, handover_count = handover_count, access_hash=artifact_hash)
	
@app.route('/handover/<handover_id>/', methods=['GET', 'POST'])
@app.route('/handover/<handover_id>/<handover_hash>', methods=['GET', 'POST'])
def handover(handover_id, handover_hash = None):
	form = UpdateForm()
	handover = Handover.query.get(handover_id)
	user = User.query.get(handover.user_id)
	text = Text.query.join(Media).filter(Media.id == Text.media_id).join(Handover).filter(Media.id == Handover.media_id).filter(Handover.id == handover_id).limit(1)
	handover_count = Handover.query.filter(Handover.artifact_id==handover.artifact_id).count()
	print("text")
	print (text[0].text)
	if handover == None: 
		return redirect(url_for('index'))
	if handover_hash is not None and handover.access_hash == handover_hash:
		editable = True
		form.email = user.email 
		form.text = text.text
		form.name = user.name
	else: 
		editable = False
	if form.validate_on_submit():
		user.email = form.email.data
		if handover.media_id != None:
			media = Media.query.get(handover.media_id)
		db.session.commit()
	return render_template('handover.html',title = "Show Handover", handover = handover, text=text[0], username = user.name, email = user.email, artifact_id = handover.artifact_id, handover_count = handover_count)


