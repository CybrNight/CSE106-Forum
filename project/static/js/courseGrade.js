class GradesApp {

    constructor(gradesTable) {
        this.gradesTable = gradesTable
    }

    async showAllGrades() {
        const This = this;
        console.log(course)
        let response = await fetch(`/courses/${courseId}/students`, {
            method: "GET"
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();
            console.log(json)



            //Delete all rows in the grades view table
            for (var i = 1; i < this.gradesTable.rows.length;) {
                console.log("Deleted row:" + this.gradesTable.rows[i]);
                this.gradesTable.deleteRow(i);
            }
            for (var counter in json.counters) {
                console.log(json.counters[counter].counter_name);
            }

            //Add new rows to the table
            console.log(json)
            Object.keys(json).forEach(async key => {
                const student = json[key];

                //Insert row and two cells
                const row = This.gradesTable.insertRow();
                const studentsCell = row.insertCell();
                const gradeCell = row.insertCell();
                gradeCell.setAttribute('contenteditable', 'true')


                //Set the cell values to the name (key) and grade (json[key])
                studentsCell.innerText = student.name;
                gradeCell.innerText = student.grade;
                row.id = student.id;
            });
        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async saveGrades() {
        var rows = this.gradesTable.rows;
        var grades = [];
        for (var i = 1; i < rows.length; i++) {
            const grade = rows[i].cells[1].innerText;

            if (parseInt(grade) < 0 || parseInt(grade) > 100) {
                alert("Grade value must be between 0 and 100")
                return;
            }

            const user_id = rows[i].id;
            grades.push({ [user_id]: grade });
        }
        console.log(grades);
        fetch(`/courses/${courseId}/students`, {
            method: 'PUT',
            body: JSON.stringify(grades),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                console.log("Success");
                alert("Successfully saved grades data!");
            } else {
                throw new Error("Error");
            }
        }).catch(error => {
            console.log(error);
        });
    }
}
window.onload = function () {
    const gradesTable = document.getElementById('grades-table');
    const btnSaveGrades = document.getElementById('btn-save-grades');

    c = new GradesApp(gradesTable);

    btnSaveGrades.addEventListener('click', button => {
        c.saveGrades();
    });
    c.showAllGrades();
}

function courseTabs(event, tabAction) {
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabAction).style.display = "block";
    event.currentTarget.className += " active";
}

function goBack() {
    window.location.href = "/courses";
}

//post grades to database using @ main.route('/courses/<c_name>/students', methods=['POST']
