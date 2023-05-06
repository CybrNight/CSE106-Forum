
class PostView {

    constructor(postTitle, postContent) {
        this.postTitle = postTitle;
        this.postContent = postContent;
    }

    async getPostContent() {

    }
}

function updatePostButton(postBox, postTitle, btnPost) {
    if (postBox.value && postTitle.value) {
        btnPost.disabled = false
    } else {
        btnPost.disabled = true
    }
}

window.onload = function () {
    const postBox = document.getElementById("textarea-post-content");
    const postTitle = document.getElementById("input-post-title");
    const postContent = document.getElementById("post-content")
    const btnPost = document.getElementById("btn-post-create")

    c = new PostView(postTitle, postContent);

    updatePostButton(postBox, postTitle, btnPost);

    postTitle.addEventListener('input', event => updatePostButton(postBox, postTitle, btnPost));
    postBox.addEventListener('input', event => updatePostButton(postBox, postTitle, btnPost));
    //c.getPostContent()
}