submitlogin.addEventListener("click", async function(event) {
    //Avoid refreshing page
    event.preventDefault();
    //Take username and password from input fields, send to app.py and wait for it to respond
    let response = await window.fetch(`/login?username=${username.value.trim()}`);
    response = await response.json()
    console.log(response)
    if (response.type == "success") {
        msg.textContent = "Login successful";
        console.log("Login successful")
    } else if (response.type == "failure") {
        msg.textContent = "Login failed";
    } else {
        console.log("not working")
    }
})