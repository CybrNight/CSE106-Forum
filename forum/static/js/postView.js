
class PostView {

    constructor(btnUpvote, btnDownvote, replyBox) {
        this.btnUpvote = btnUpvote;
        this.btnDownvote = btnDownvote;
        this.postCount = document.getElementById("post-vote-count");
        this.replyBox = replyBox;
    }

    async upvotePost() {
        const uuid = post.uuid;
        const uri = post.uri;

        let response = await fetch(`/posts/${uuid}/${uri}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "vote-type": "UP" })
        });

        if (response.ok) {
            const data = await response.json();
            this.postCount.innerText = data.votes;

            if (!$("#post-upvote").hasClass("upvote")) {
                $("#post-upvote").addClass("upvote");
            } else {
                $("#post-upvote").removeClass("upvote");
            }

            if ($("#post-downvote").hasClass("downvote")) {
                $("#post-downvote").removeClass("downvote");
            }
        }
    }

    updateReplyButton() {
        if (this.replyBox.value) {
            $("#btn-post-reply").disabled = false
        } else {
            $("#btn-post-reply").disabled = true
        }
    }

    async downvotePost() {
        const uuid = post.uuid;
        const uri = post.uri;

        let response = await fetch(`/posts/${uuid}/${uri}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "vote-type": "DOWN" })
        });

        if (response.ok) {
            const data = await response.json();
            this.postCount.innerText = data.votes;

            if (!$("#post-downvote").hasClass("downvote")) {
                $("#post-downvote").addClass("downvote");
            } else {
                $("#post-downvote").removeClass("downvote");
            }

            if ($("#post-upvote").hasClass("upvote")) {
                $("#post-upvote").removeClass("upvote");
            }
        }
    }
}

window.onload = function () {
    const replyBox = document.getElementById("textarea-post-reply");

    const btnUpvote = document.getElementById("post-upvote");
    const btnDownvote = document.getElementById("post-downvote");

    postView = new PostView(btnUpvote, btnDownvote, replyBox);

    console.log(post.userVote)
    if (post.userVote === "DOWN") {
        $("#post-downvote").addClass("downvote");
    } else if (post.userVote === "UP") {
        $("#post-upvote").addClass("upvote");
    }

    btnUpvote.addEventListener('mouseup', button => {
        postView.upvotePost();
    });

    btnDownvote.addEventListener('mouseup', button => {
        postView.downvotePost();
    });

    $("#btn-post-reply").disabled = true
    replyBox.oninput = postView.updateReplyButton();
    replyBox.onchange = postView.updateReplyButton();
}