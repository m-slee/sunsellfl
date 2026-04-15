console.log("notification.js");
const notifications = document.querySelectorAll(".notification");
const notificationCloses = document.querySelectorAll(".notification-close");

if (notificationCloses) {
    [...notificationCloses].forEach((notificationClose, i) => {
        notificationClose.addEventListener("click", () => {
            notifications[i].remove();
        })
    });
}