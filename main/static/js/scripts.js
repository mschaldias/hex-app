
function toggleSidebar(){
    var sidebar = document.querySelector("#sidebar");
    var container = document.querySelector(".my-container");
    sidebar.classList.toggle("active-nav");
    container.classList.toggle("active-cont");
}

function setTimeZone() {
    // Timezone settings
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone; // e.g. "America/New_York"
    document.cookie = "django_timezone=" + timezone;
}


