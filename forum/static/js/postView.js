
class PostView {

    constructor(btnUpvote, btnDownvote, replyBox) {
        this.btnUpvote = btnUpvote;
        this.btnDownvote = btnDownvote;
        this.voteCount = document.getElementById("post-vote-count");
        this.replyBox = replyBox;
        this.replyBtn = document.getElementById("btn-post-reply");

        this.upvote = $('#post-upvote');
        this.downvote = $("#post-downvote");
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
            this.voteCount.innerText = data.votes;

            const up = voteType == "UP"
            const down = voteType == "DOWN"

            if (up) {
                if (this.upvote.hasClass("upvote")) {
                    this.upvote.removeClass("upvote");
                } else {
                    this.upvote.addClass("upvote");
                }
                this.downvote.removeClass("downvote");
            } else if (down) {
                if (this.downvote.hasClass("downvote")) {
                    this.downvote.removeClass("downvote");
                } else {
                    this.downvote.addClass("downvote");
                }
                this.upvote.removeClass("upvote");
            }

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
    const upvote = $(`#btn-upvote-${uuid}`);
    const downvote = $(`#btn-downvote-${uuid}`);

    if (replyVote(uuid, uri, "UP")) {
        if (upvote.hasClass("upvote")) {
            upvote.removeClass("upvote");
        } else {
            upvote.addClass("upvote");
        }

        downvote.removeClass("downvote");
    }
}

async function downvoteReply(uuid, uri) {
    const upvote = $(`#btn-upvote-${uuid}`);
    const downvote = $(`#btn-downvote-${uuid}`);

    if (replyVote(uuid, uri, "DOWN")) {
        if (downvote.hasClass("downvote")) {
            downvote.removeClass("downvote");
        } else {
            downvote.addClass("downvote");
        }

        upvote.removeClass("upvote");
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
        return true;
    }
    return false;
}

window.onload = function () {
    const replyBox = document.getElementById("textarea-post-reply");

    const btnUpvote = document.getElementById("post-upvote");
    const btnDownvote = document.getElementById("post-downvote");

    postView = new PostView(btnUpvote, btnDownvote, replyBox);

    if (post.voteType === "DOWN") {
        $("#post-downvote").addClass("downvote");
    } else if (post.voteType === "UP") {
        $("#post-upvote").addClass("upvote");
    }

    btnUpvote.addEventListener('mouseup', button => {
        postView.postVote("UP");
    });

    btnDownvote.addEventListener('mouseup', button => {
        postView.postVote("DOWN");
    }, true);

    postView.updateReplyButton()
    replyBox.addEventListener('input', event => postView.updateReplyButton());
}