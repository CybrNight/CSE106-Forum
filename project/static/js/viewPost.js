class PostView {

    constructor(postTitle, postContent) {
        this.postTitle = postTitle;
        this.postContent = postContent;
    }

    async getPostContent() {
        let response = await fetch("/getpost", {
            method: "GET"
        });

        if (response.ok) {
            const post = await response.json();

            //this.postContent.innerText = post.content;
            //this.postTitle.innerText = post.title;
        } else {
            throw new InternalError(`${response.status}:Unexpected error`);
        }
    }
}

window.onload = function () {
    const postTitle = document.getElementById("post-title");
    const postContent = document.getElementById("post-content")

    c = new PostView(postTitle, postContent);

    //c.getPostContent()
}