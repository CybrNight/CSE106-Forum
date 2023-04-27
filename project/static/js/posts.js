class CourseApp {

    constructor(courseTable, enrolledTable) {
        this.courseTable = courseTable;
        this.enrolledTable = enrolledTable;
    }

    async getCourseTable() {
        const This = this;
        let response = await fetch("/getCourses", {
            method: "GET"
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();



            //Delete all rows in the grades view table
            for (var i = 1; i < this.courseTable.rows.length;) {
                console.log("Deleted row:" + this.courseTable.rows[i]);
                this.courseTable.deleteRow(i);
            }
            for (var counter in json.counters) {
                console.log(json.counters[counter].counter_name);
            }

            //Add new rows to the table
            console.log(json)
            Object.keys(json).forEach(async key => {
                const course = json[key];

                //Insert row and two cells
                const row = This.courseTable.insertRow();
                const courseNameCell = row.insertCell();
                const profCell = row.insertCell();
                const timeCell = row.insertCell();
                const studentsCell = row.insertCell();
                const addCell = row.insertCell();

                //Set the cell values to the name (key) and grade (json[key])
                courseNameCell.innerText = course.courseName;
                profCell.innerText = course.prof;
                timeCell.innerText = course.time;
                studentsCell.innerText = `${course.enrolled} / ${course.maxEnroll}`;
                const in_class = course.in_class;

                const btn = document.createElement('button');
                if (course.enrolled < course.maxEnroll) {
                    if (!in_class) {
                        btn.onmouseup = async () => {
                            await this.addCourse(course.courseId);
                        };
                        btn.className = "fa-sharp fa-solid fa-plus";
                        addCell.appendChild(btn);
                    } else {
                        btn.className = "fa-sharp fa-solid";
                        btn.innerText = "ENROLLED";
                        btn.disabled = true;
                        addCell.appendChild(btn);
                    }
                } else {
                    btn.className = "fa-sharp fa-solid";
                    if (!in_class)
                        btn.innerText = "FULL";
                    else
                        btn.innerText = "ENROLLED";
                    btn.disabled = true;
                    addCell.appendChild(btn);
                }
            });
        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async getEnrolledTable() {
        const This = this;
        let response = await fetch("/getEnrolled", {
            method: "GET"
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();



            //Delete all rows in the grades view table
            for (var i = 1; i < this.enrolledTable.rows.length;) {
                console.log("Deleted row:" + this.enrolledTable.rows[i]);
                this.enrolledTable.deleteRow(i);
            }
            for (var counter in json.counters) {
                console.log(json.counters[counter].counter_name);
            }

            //Add new rows to the table
            console.log(json)
            Object.keys(json).forEach(key => {
                const course = json[key];

                //Insert row and two cells
                var row = This.enrolledTable.insertRow();
                var courseNameCell = row.insertCell();
                var profCell = row.insertCell();
                var timeCell = row.insertCell();
                var studentsCell = row.insertCell();
                var removeCell = row.insertCell();

                //Set cell values to the course information
                courseNameCell.innerText = course.courseName;
                profCell.innerText = course.prof;
                timeCell.innerText = course.time;
                studentsCell.innerText = `${course.enrolled} / ${course.maxEnroll}`;

                //Add remove course button
                const btn = document.createElement('button');
                btn.onmouseup = async () => {
                    console.log(course.id)
                    await this.removeCourse(course.courseId);
                };
                btn.innerHTML = "<i></i>";
                btn.className = "fa-sharp fa-solid fa-minus";
                removeCell.appendChild(btn);
            });
        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }

    async addCourse(courseId) {
        let response = await fetch('/courses/add', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "courseId": courseId })
        });
        if (response.ok) {
            await this.getEnrolledTable();
            await this.getCourseTable();
        } else {
            throw new InternalError(`${response.status}:Unexpected error`);
        }

    }

    async removeCourse(courseId) {
        let response = await fetch(`/courses/remove/${courseId}`, {
            method: "DELETE",
            body: JSON.stringify({ "courseId": courseId })
        });
        if (response.ok) {
            await this.getEnrolledTable();
            await this.getCourseTable();
        } else {
            if (response.status === 404) {
                throw new Error("Student not enrolled in course " + courseId);
            }
            throw InternalError("Unexpected response" + response.status);
        }
    }
}
window.onload = function () {
    const courseTable = document.getElementById('course-table');
    const enrolledTable = document.getElementById('enrolled-table');
    console.log(courseTable === null)

    c = new CourseApp(courseTable, enrolledTable);

    c.getCourseTable().catch(error => {
        console.log(error);
    });

    c.getEnrolledTable().catch(error => {
        console.log(error);
    })
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
