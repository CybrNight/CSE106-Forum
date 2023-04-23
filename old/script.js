function isNumeric(str) {
    if (typeof str != "string") return false // we only process strings!  
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
        !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
}

class App {
    constructor(gradesOutput, gradesTable) {
        this.debug = true;
        this.gradesOutput = gradesOutput;
        this.gradesTable = gradesTable;
        this.currentStudent = undefined;
        this.currentGrade = undefined;
    }

    //Updates the table in the app to show all the grade
    async showAllGrades() {
        console.log("Called showAllGrades()");
        const This = this;

        //Setup fetch GET request
        let response = await fetch("/grades", {
            method: "GET",
            headers: {
                'Accept': 'application/json',
            }
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();

            //Delete all rows in the grades view table
            for (var i = 1; i < this.gradesTable.rows.length;) {
                console.log("Deleted row:" + this.gradesTable.rows[i]);
                this.gradesTable.deleteRow(i);
            }

            //Add new rows to the table
            Object.keys(json).forEach(function (key) {

                //Insert row and two cells
                var row = This.gradesTable.insertRow();
                var cell = row.insertCell();
                var cell1 = row.insertCell();

                //Set the cell values to the name (key) and grade (json[key])
                cell.innerText = key;
                cell1.innerText = json[key];
                console.log();
            });
        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async getGrade(sName) {
        let response = await fetch(`/grades/${sName.replace(" ", "%20")} `, {
            method: "GET"
        });

        if (response.ok) {
            console.log("Response:" + response.status)
            console.log("Get grade of " + sName);
            let json = await response.json();

            //Set value of the current student and grade
            this.currentStudent = sName;
            this.currentGrade = json[sName];
            grades.updateOutput();
        } else {
            //Show error is student doesn't exist in record
            if (response.status === 404) {
                console.log(await response.statusText);
                throw new Error(`${await response.text()}`);
            }
            throw InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async editGrade(sName, sGrade) {
        //Show error if user tries to enter string or negative
        if (!isNumeric(sGrade) || parseFloat(sGrade) < 0) {
            this.statusAlert("Grade must be a number >= 0");
            return;
        }

        let response = await fetch(`/grades/${sName.replace(" ", "%20")} `, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "grade": sGrade })
        });

        if (response.ok) {
            console.log("Edit grade " + sName);
            this.showAllGrades();
            this.getGrade(sName);
        } else {
            if (response.status === 404) {
                throw new Error(`${await response.text()}`);
            }
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async addGrade(sName, sGrade) {
        if (!isNumeric(sGrade) || parseFloat(sGrade) < 0) {
            throw new TyoeError(`${await response.text()}`);
        }

        let response = await fetch('/grades', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "name": sName, "grade": sGrade })
        });

        if (response.ok) {
            this.statusAlert(`Successfully added new student (${sName})`);
            this.showAllGrades();
            console.log("Add grade " + sName);
        } else {
            if (response.status === 409) {
                throw new Error(`${await response.text()}`);
            }

            throw InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async deleteStudent(sName) {
        let response = await fetch(`/grades/${sName.replace(" ", "%20")}`, {
            method: "DELETE",
        });

        if (response.ok) {
            console.log("Delete grade " + sName);
            this.showAllGrades();
            this.statusAlert("Deleted Student")
        } else {
            if (response.status === 404) {
                throw new Error(`${await response.text()}`);
            }

            throw InternalError(`${response.status}:${await response.text()}`);
        }
    }

    handleError(error) {
        if (error.constructor !== InternalError) {
            this.statusAlert(error.message)
        } else {
            alert(error.message);
        }
    }

    updateOutput() {
        if (this.currentGrade === undefined) return;

        this.gradesOutput.innerText = this.currentStudent + "\n" + this.currentGrade;
    }

    statusAlert(status) {
        this.gradesOutput.innerText = status;
    }
}

const btnGetStudents = document.getElementById('btn-get-students');
const btnGetGrade = document.getElementById('btn-get-grade');
const btnGradeJSON = document.getElementById('btn-grade-json');
const bntAddGrade = document.getElementById('btn-add-grade');
const btnEditGrade = document.getElementById('btn-edit-grade');
const btnDelGrade = document.getElementById('btn-del-grade');

const fldStudentName = document.getElementById('fld-student-name');
const fldStudentGrade = document.getElementById('fld-student-grade');

const txtGradesOutput = document.getElementById('div-grades-output');
const tblGradesOutput = document.getElementById('grades-table');

grades = new App(txtGradesOutput, tblGradesOutput);

btnGetGrade.addEventListener('click', button => {
    const sName = fldStudentName.value;
    grades.getGrade(sName).catch(error => {
        grades.handleError(error);
    });
});

btnGetStudents.addEventListener('click', button => {
    grades.showAllGrades().catch(error => {
        grades.handleError(error);
    });
})

bntAddGrade.addEventListener('click', button => {
    const sName = fldStudentName.value;
    const sGrade = fldStudentGrade.value;
    grades.addGrade(sName, sGrade).catch(error => {
        grades.handleError(error);
    });
})

btnEditGrade.addEventListener('click', button => {
    const sName = fldStudentName.value;
    const sGrade = fldStudentGrade.value;
    grades.editGrade(sName, sGrade).catch(error => {
        grades.handleError(error);
    });
});

btnDelGrade.addEventListener('click', button => {
    const sName = fldStudentName.value;
    grades.deleteStudent(sName).catch(error => {
        grades.handleError(error);
    });
})

grades.showAllGrades();