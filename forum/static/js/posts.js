class CourseApp {

    constructor(postTable) {
        this.postTable = postTable;
    }

    async getPostTable() {
        const This = this;
        let response = await fetch("/getPosts", {
            method: "GET"
        });
        if (response.ok) {
            //Get json payload
            const json = await response.json();


            //Delete all rows in the grades view table
            for (var i = 1; i < this.postTable.rows.length;) {
                console.log("Deleted row:" + this.postTable.rows[i]);
                this.postTable.deleteRow(i);
            }
            for (var counter in json.counters) {
                console.log(json.counters[counter].counter_name);
            }
            //Add new rows to the table
            console.log(json)
            Object.keys(json).forEach(key => {
                const post = json[key];
                //Insert row and two cells
                var row = This.postTable.insertRow();
                var postTitleCell = row.insertCell();
                var postAuthorCell = row.insertCell();
                var postDateCell = row.insertCell();
                var postUpvotesCell = row.insertCell();
                var postTagCell = row.insertCell();

                //Set cell values to the course information
                postTitleCell.innerHTML = `<a href="/posts/${post.uuid}/${post.title}/">${post.title}</a>`;
                postAuthorCell.innerText = post.author;
                postDateCell.innerText = post.date;
                postUpvotesCell.innerText = post.votes;
                postTagCell.innerText = post.tags;
            });
        } else {
            throw new InternalError(`${response.status}:${await response.text()}`);
        }
    }
}
window.onload = function () {
    const postTable = document.getElementById('posts-table');

    c = new CourseApp(postTable);

    c.getPostTable().catch(error => {
        console.log(error);
    });
}

function posts(event, tabAction) {
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
