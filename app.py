from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "employee_salary_secret"

UPLOAD_FOLDER = "uploads"
DEFAULT_CSV = "data/employees.csv"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# Load CSV Data
# ----------------------------
def load_data():
    upload_file = os.path.join(app.config["UPLOAD_FOLDER"], "employees.csv")

    if os.path.exists(upload_file):
        return pd.read_csv(upload_file)

    return pd.read_csv(DEFAULT_CSV)


def get_csv_path():
    upload_file = os.path.join(app.config["UPLOAD_FOLDER"], "employees.csv")

    if os.path.exists(upload_file):
        return upload_file

    return DEFAULT_CSV


# ----------------------------
# Home Page
# ----------------------------
@app.route("/")
def home():

    df = load_data()

    total_employees = len(df)
    average_salary = int(df["Salary"].mean())
    highest_salary = int(df["Salary"].max())
    lowest_salary = int(df["Salary"].min())

    return render_template(
        "index.html",
        total_employees=total_employees,
        average_salary=average_salary,
        highest_salary=highest_salary,
        lowest_salary=lowest_salary
    )


# ----------------------------
# Employees Page
# ----------------------------
@app.route("/employees")
def employees():

    df = load_data()

    employees_data = df.to_dict(orient="records")

    return render_template(
        "employees.html",
        employees=employees_data
    )


# ----------------------------
# Analytics Page
# ----------------------------
@app.route("/analytics")
def analytics():

    df = load_data()

    # Average Salary by Department
    dept_salary = df.groupby("Department")["Salary"].mean()

    # Employees by Department
    dept_count = df.groupby("Department").size()

    # Experience Distribution
    experience = df.groupby("Experience").size()

    # Top 5 Salaries
    top_salary = df.sort_values(
        by="Salary",
        ascending=False
    ).head(5)

    return render_template(

        "analytics.html",

        dept_labels=dept_salary.index.tolist(),
        dept_values=[float(x) for x in dept_salary.values],

        count_labels=dept_count.index.tolist(),
        count_values=[int(x) for x in dept_count.values],

        exp_labels=[str(x) for x in experience.index.tolist()],
        exp_values=[int(x) for x in experience.values],

        top_labels=top_salary["Name"].tolist(),
        top_values=[int(x) for x in top_salary["Salary"].tolist()]

    )


# ----------------------------
# Upload CSV
# ----------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        if "file" not in request.files:
            flash("No file selected!", "danger")
            return redirect("/upload")

        file = request.files["file"]

        if file.filename == "":
            flash("Please choose a CSV file.", "danger")
            return redirect("/upload")

        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are allowed.", "danger")
            return redirect("/upload")

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], "employees.csv"))

        flash("CSV uploaded successfully!", "success")

        return redirect("/")

    return render_template("upload.html")


# ----------------------------
# Add Employee
# ----------------------------
@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        df = load_data()

        new_employee = {

            "EmployeeID": len(df) + 101,
            "Name": request.form["name"],
            "Department": request.form["department"],
            "Experience": request.form["experience"],
            "Salary": request.form["salary"]

        }

        df = pd.concat(
            [df, pd.DataFrame([new_employee])],
            ignore_index=True
        )

        df.to_csv(get_csv_path(), index=False)

        flash("Employee added successfully!", "success")

        return redirect("/employees")

    return render_template("add_employee.html")


# ----------------------------
# About Page
# ----------------------------
@app.route("/about")
def about():
    return render_template("about.html")


# ----------------------------
# Run Application
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)