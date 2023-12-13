from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Hashtag
from . import db
import json
from datetime import datetime

views = Blueprint('views', __name__)


def notes_modificate(text):
    no_hashtags = []
    only_hashtags = []
    splited_by_space = text.split()
    for word in splited_by_space:
        if word[0] == "#":
            if len(word) > 1:
                only_hashtags.append(word[1:])
        else:
            no_hashtags.append(word)
    only_hashtags = [*set(only_hashtags)]
    no_hashtags = ' '.join(no_hashtags)
    return no_hashtags, only_hashtags


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        note = request.form.get("note")
        plain_text, hashtags = notes_modificate(note)
        category = request.form.get("category")
        day = request.form.get("day")
        if len(plain_text) < 1:
            flash("Note is too short!", category="error")
        else:
            db_hashtags = []
            for hashtag in hashtags:
                db_hashtag = Hashtag.query.filter_by(value=hashtag, user_id=current_user.id).first()
                if db_hashtag:
                    db_hashtags.append(db_hashtag)
                else:
                    new_hashtag = Hashtag(value=hashtag, user_id=current_user.id)
                    db.session.add(new_hashtag)
                    db.session.commit()
                    db_hashtags.append(new_hashtag)

            new_note = Note(data=plain_text,
                            user_id=current_user.id,
                            complete=False,
                            category=category,
                            day=day,
                            hashtags=db_hashtags,
                            raw_text=note)
            db.session.add(new_note)
            db.session.commit()
            flash("Note added", category="success")

    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, current_time=datetime.now(), hashtags=db_hashtags)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash("Task deleted", category="error")
    return jsonify({})


@views.route('/mark_update', methods=["POST"])
def mark_update():
    note = json.loads(request.data)  # do note przypisz to co w js jest w body (data=body)
    noteId = note[
        'noteId']  # do nazyw noteId przypisz id tego taska (noteId==note.id w home.html) z dic, ktory zrobiłsie wczesniej dic-> note ={noteId: 3}
    note = Note.query.get(noteId)  # no tu przypisze ten id ktory znalazl, poprostu nadpisuje nazwe note
    if note:
        if note.user_id == current_user.id:
            note.complete = not note.complete
            db.session.commit()
            if note.complete:
                flash("This task is done! Good job! ", category="success")
            else:
                flash("This task is undone! Try harder! ", category="error")
    return jsonify({})


@views.route('/mark_important', methods=["POST"])
def mark_important():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            note.important = not note.important
            db.session.commit()
            if note.important:
                flash("KEEP AN EYE ON IT !")
            else:
                flash("keep going")
    return jsonify({})


@views.route('/edit-note', methods=['POST'])
def edit_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    raw_text = note['updatedNoteData']
    plain_text, hashtags = notes_modificate(raw_text)

    db_hashtags = []
    for hashtag in hashtags:
        db_hashtag = Hashtag.query.filter_by(value=hashtag, user_id=current_user.id).first()
        if db_hashtag:
            db_hashtags.append(db_hashtag)
        else:
            new_hashtag = Hashtag(value=hashtag, user_id=current_user.id)
            db.session.add(new_hashtag)
            db.session.commit()
            db_hashtags.append(new_hashtag)

    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            note.data = plain_text  # note.data to jest (note zobacz wyzej zaciągnełaś juz ze to obecna notatka, .data to z formatki w models) wiec do starej notatki przypisz nową wzięta z dicta z js
            note.raw_text = raw_text
            note.hashtags = db_hashtags
            db.session.commit()
            flash('Task updated', category="success")
    return jsonify()


@views.route('/category')
@login_required
def cat_home():
    category_name = request.args.get("name")
    notes = Note.query.filter_by(user_id=current_user.id).all()
    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()

    filtered_notes = []
    for note in notes:
        if note.category == category_name:
            filtered_notes.append(note)

    return render_template("bookmark.html", category=category_name, notes=filtered_notes, user=current_user,
                           current_time=datetime.now(), hashtags=db_hashtags, titles=category_name.capitalize())


@views.route('/hashtag')
@login_required
def get_by_hashtag():
    hashtag_name = request.args.get("name")
    db_hashtag = Hashtag.query.filter_by(value=hashtag_name, user_id=current_user.id).first()
    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()

    if db_hashtag is None:
        return flash("No hashtag found!", category="error")

    notes = db_hashtag.Notes.all()

    return render_template("bookmark.html", notes=notes, user=current_user,
                           current_time=datetime.now(), hashtags=db_hashtags, titles=hashtag_name.capitalize())


@views.route('/delete_hashtag_bookmark', methods=['POST'])
def delete_hashtag_bookmark():
    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()

    for db_hashtag in db_hashtags:
        notes = db_hashtag.Notes.all()
        if len(notes) < 1:
            db.session.delete(db_hashtag)
            db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/day')
@login_required
def day():
    choose_day = request.args.get("name")
    all_notes = Note.query.filter_by(user_id=current_user.id).all()
    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()

    day_notes = []
    for note in all_notes:
        ddy = note.day
        if ddy == choose_day:
            day_notes.append(note)

    return render_template("bookmark.html", day=choose_day, user=current_user, notes=day_notes,
                           current_time=datetime.now(), hashtags=db_hashtags, titles=choose_day.capitalize())


@views.route('/search')
@login_required
def search():
    all_notes = Note.query.filter_by(user_id=current_user.id).all()
    db_hashtags = Hashtag.query.filter_by(user_id=current_user.id).all()

    search_item = request.args.get("search")
    searched_tasks = []

    for note in all_notes:
        text = note.data
        ser = str(search_item).lower()
        if ser in text:
            searched_tasks.append(note)

    return render_template("bookmark.html", user=current_user, notes=searched_tasks,
                           current_time=datetime.now(), hashtags=db_hashtags,
                           titles=f"All tasks containing word: {search_item}")
