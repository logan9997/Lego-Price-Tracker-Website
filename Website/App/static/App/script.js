window.onload = function() {
    document.addEventListener("DOMContentLoaded", function(event) { 
        var scrollpos = localStorage.getItem('scrollpos');
        if (scrollpos) window.scrollTo(0, scrollpos);
    });

    window.onbeforeunload = function(e) {
        localStorage.setItem('scrollpos', window.scrollY);
    };
}

function display_item_delete_quantity() {
    form = document.getElementsByClassName("")
}

function logout_popup(e) {
    if (confirm("Are you sure?")) {
        window.location.reload()
    } else {
        e.preventDefault()
    }
}


function show_dropdown_content() {
    var element_style = document.getElementById("dropdown-content").style.display;
    console.log(element_style)
    if (element_style == "flex") {
        document.getElementById("dropdown-content").style.display = "none";
    } else {
        document.getElementById("dropdown-content").style.display = "flex";
    }
}


function reveal_sub_themes(theme_path) {
    if (theme_path.style.display == "none") {
        theme_path.style.display = "block";
    } else {
        theme_path.style.display = "none";  
    }
}
