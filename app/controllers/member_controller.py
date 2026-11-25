from flask import Blueprint, render_template, request, redirect, session, jsonify
import sqlite3
from ..models.member_model import *

member_bp = Blueprint("member", __name__)

SOCIETIES = ["UMT IEEE", "UMT ACM", "UMT CSS", "UMT IEEE-WIE", "UMT Robotics", "UMT Cybersecurity"]
GENDERS = ["Male", "Female", "Other"]
POSITIONS = ["Member", "Volunteer", "President", "Vice President", "Treasurer", "Secretary"]

@member_bp.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        session["user"] = "admin"

    results = []
    message = ""
    show_results = False

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            try:
                data = (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["gender"],
                    request.form["student_id"],
                    request.form["society"],
                    request.form["date_joined"],
                    request.form["position"]
                )
                add_member(data)
                message = "Member added successfully!"
                results = find_by_society(request.form["society"])
                show_results = True
            except sqlite3.IntegrityError:
                message = "Error: Student ID already exists!"
        elif action == "find_id":
            results = find_by_student_id(request.form["student_id"])
            show_results = True
        elif action == "find_society":
            results = find_by_society(request.form["society"])
            show_results = True

    return render_template("home.html", societies=SOCIETIES, genders=GENDERS, positions=POSITIONS, results=results, message=message, show_results=show_results)

@member_bp.route("/update_member", methods=["POST"])
def update_route():
    current_id = request.form.get("current_id")
    update_data = {
        "student_id": request.form.get("new_student_id"),
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "position": request.form.get("position")
    }
    filtered_data = {k: v for k, v in update_data.items() if v}
    update_student_member_information(current_id, filtered_data)
    return redirect("/home")

@member_bp.route("/delete_member", methods=["POST"])
def delete_route():
    delete_student_member_information(request.form.get("student_id"))
    return redirect("/home")

@member_bp.route("/sort_results", methods=["POST"])
def sort_route():
    results = get_all_members()  
    sorted_res = sort_search_results(results, request.form.get("sort_by"), request.form.get("order"))
    return render_template("home.html", societies=SOCIETIES, genders=GENDERS, positions=POSITIONS, results=sorted_res, show_results=True)

@member_bp.route("/view_graph")
def view_graph():
    return jsonify(view_all_member_using_graph())