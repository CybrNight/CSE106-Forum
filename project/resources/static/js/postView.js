
class PostView {

    constructor(postTitle, postContent) {
        this.postTitle = postTitle;
        this.postContent = postContent;
    }

    async getPostContent() {

    }
}

window.onload = function () {
    const postTitle = document.getElementById("post-title");
    const postContent = document.getElementById("post-content")

    c = new PostView(postTitle, postContent);

    //c.getPostContent()
}