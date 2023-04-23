class CourseApp {

    constructor(teacherTable, gradesTable) {
        this.teacherTable = teacherTable;
        this.gradesTable = gradesTable;
    }

    async getTeacherTable() {
        const This = this;
        let response = await fetch("/getEnrolled", {
            method: "GET"
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();



            //Delete all rows in the grades view table
            for (var i = 1; i < this.teacherTable.rows.length;) {
                console.log("Deleted row:" + this.teacherTable.rows[i]);
                this.teacherTable.deleteRow(i);
            }
            for (var counter in json.counters) {
                console.log(json.counters[counter].counter_name);
            }

            //Add new rows to the table
            console.log(json)
            Object.keys(json).forEach(key => {
                const course = json[key];

                //Insert row and two cells
                //check if course.prof is the same as the logged in user
                console.log(course)
                if (true) {
                    var row = This.teacherTable.insertRow();
                    var courseNameCell = row.insertCell();
                    var timeCell = row.insertCell();
                    var studentsCell = row.insertCell();

                    //Set the cell values to the name (key) and grade (json[key])

                    // course button for courses/courseName
                    courseNameCell.innerHTML = '<a href="/courses/' + course.courseId + '">' + course.courseName + '</a>';
                    timeCell.innerText = course.time;
                    studentsCell.innerText = `${course.enrolled} / ${course.maxEnroll}`;
                }
            });

        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    // async getGradesTable() {
    //     const This = this;
    //     let response = await fetch("/getGrades", {
    //         method: "GET"
    //     });
    //     if (response.ok) {
    //         //Get json payload
    //         const json = await response.json();



    //         //Delete all rows in the grades view table
    //         for (var i = 1; i < this.courseTable.rows.length;) {
    //             console.log("Deleted row:" + this.courseTable.rows[i]);
    //             this.courseTable.deleteRow(i);
    //         }
    //         for (var counter in json.counters) {
    //             console.log(json.counters[counter].counter_name);
    //         }

    //         //Add new rows to the table
    //         console.log(json)
    //         Object.keys(json).forEach(key => {
    //             const course = json[key];

    //             //Insert row and two cells
    //                 var row = This.courseTable.insertRow();
    //                 var studentCell = row.insertCell();
    //                 var gradeCell = row.insertCell();

    //                 //Set the cell values to the name (key) and grade (json[key])
    //                 studentCell = student.name;
    //                 gradeCell = student.grade;
    //         });
    //     } else {
    //         throw new InternalError(`${response.status}:${await response.text()}`);
    //     }
    // }
}
window.onload = function () {
    const teacherTable = document.getElementById('teacher-table');
    const gradesTable = document.getElementById('grades-table');
    console.log(teacherTable === null)

    c = new CourseApp(teacherTable, gradesTable);

    c.getTeacherTable().catch(error => {
        console.log(error);
    });

    // c.getGradesTable().catch(error => {
    //     console.log(error);
    // });
}

const getCookie = (name) => (
    (document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || '').replaceAll('"', "")
)

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
