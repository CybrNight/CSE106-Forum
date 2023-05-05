
class PostView {

    constructor(btnUpvote, btnDownvote, replyBox) {
        this.btnUpvote = btnUpvote;
        this.btnDownvote = btnDownvote;
        this.postCount = document.getElementById("post-vote-count");
        this.replyBox = replyBox;
        this.replyBtn = document.getElementById("btn-post-reply");

        this.upvote = $('#post-upvote');
        this.downvote = $("#post-downvote");
    }

    async upvotePost() {
        if (this.postVote("UP")) {
            if (this.upvote.hasClass("upvote")) {
                this.upvote.removeClass("upvote");
            } else {
                this.upvote.addClass("upvote");
            }

            this.downvote.removeClass("downvote");
        }
    }

    async downvotePost() {
        if (this.postVote("DOWN")) {
            if (this.downvote.hasClass("downvote")) {
                this.downvote.removeClass("downvote");
            } else {
                this.downvote.addClass("downvote");
            }

            this.downvote.removeClass("upvote");
        }
    }

    async postVote(voteType) {
        const uuid = post.uuid;
        const uri = post.uri;

        let response = await fetch(`/posts/${uuid}/${uri}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "vote-type": voteType })
        });

        if (response.ok) {
            const data = await response.json();
            this.postCount.innerText = data.votes;

            return true;
        }
        return false;
    }



    updateReplyButton() {
        if (this.replyBox.value) {
            this.replyBtn.disabled = false
        } else {
            this.replyBtn.disabled = true
        }
    }


}


async function upvoteReply(uuid, uri) {
    if (replyVote(uuid, uri, "UP")) {
        const id = `reply-vote-count-${uuid}`;

        document.getElementById(id).innerText = replyVotes
    }
}

async function downvoteReply(uuid, uri) {
    if (replyVote(uuid, uri, "DOWN")) {

    }
}

async function replyVote(uuid, uri, voteType) {
    let response = await fetch(`/posts/${uuid}/${uri}/reply`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "uuid": uuid, "vote-type": voteType })
    });

    if (response.ok) {
        const data = await response.json();
        const replyVotes = data['votes']
        const id = `reply-vote-count-${uuid}`;

        document.getElementById(id).innerText = replyVotes
    }
    return true;
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
    }, true);

    postView.updateReplyButton()
    replyBox.addEventListener('input', event => postView.updateReplyButton());
}