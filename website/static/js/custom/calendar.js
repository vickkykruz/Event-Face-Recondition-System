document.addEventListener("DOMContentLoaded", function () {
        const monthNameElement = document.querySelector(".month-name");
        const daysContainer = document.querySelector(".days-container");
        const prevMonthButton = document.querySelector(".prev-month");
        const nextMonthButton = document.querySelector(".next-month");
        const userUid = daysContainer.getAttribute("data-uid");
        const userRole = daysContainer.getAttribute("data-role");
        const appointmentsContainer = document.getElementById(
          "appointments-container",
        );

        let currentDate = new Date(); // Current Date
        let broadcastTime = null;

        // Listen for the 'update_time' event from the server
        socket.on("update_time", function (data) {
          const currentDateFromServer = new Date(data.date);
          currentDate = currentDateFromServer;
          broadcastTime = data.time;

          console.log("broadcastTime: ", broadcastTime);
          console.log(
            "serverFormattedDate(currentDate): ",
            serverFormattedDate(currentDate),
          );
          console.log("userUid: ", userUid);

          // Fetch appointments for the new date
          fetchAndMarkAppointments(
            serverFormattedDate(currentDate),
            userUid,
            broadcastTime,
          );
        });

        async function fetchAndMarkAppointments(date, uid, currentTime) {
          try {
            console.log("date: ", date);
            console.log("uid: ", uid);
            console.log("currentTime: ", currentTime);
            //const response = await fetch(`/api/appointments?date=${date}&uid=${uid}&current_time=${currentTime}`);
            //const appointments = await response.json();

            appointments = [];
            console.log("appointments", appointments);
            updateCalendar(appointments);
          } catch (error) {
            console.error("Error fetching appointments:", error);
          }
        }

        function serverFormattedDate(date) {
          return date.toISOString().split("T")[0];
        }

        function updateCalendar(appointments) {
          appointments = appointments || [];

          // Get the current year and month
          const year = currentDate.getFullYear();
          const month = currentDate.getMonth();

          // Update the displayed month name
          const monthNames = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
          ];
          monthNameElement.textContent = `${monthNames[month]} ${year}`;

          // Clear the days container
          daysContainer.innerHTML = "";

          // Add the day labels (Mo, Tu, We, etc.)
          const dayLabels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];
          dayLabels.forEach((label) => {
            const dayLabelElement = document.createElement("span");
            dayLabelElement.textContent = label;
            dayLabelElement.classList.add("day");
            daysContainer.appendChild(dayLabelElement);
          });

          // Get the first day of the month
          const firstDayOfMonth = new Date(year, month, 1).getDay();

          // Get the number of days in the current month
          const daysInMonth = new Date(year, month + 1, 0).getDate();

          // Get the number of days in the previous month (to show faded days)
          const daysInPrevMonth = new Date(year, month, 0).getDate();

          // Fill the days from the previous month (if needed)
          const startingDay = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1; // Adjust for Sunday as 0
          for (let i = startingDay; i > 0; i--) {
            const dayElement = document.createElement("button");
            dayElement.textContent = daysInPrevMonth - i + 1;
            dayElement.classList.add("date", "faded");
            daysContainer.appendChild(dayElement);
          }

          // Fill the current month's days
          for (let i = 1; i <= daysInMonth; i++) {
            const dayElement = document.createElement("button");
            dayElement.textContent = i;
            dayElement.classList.add("date");
            dayElement.style.position = "relative";

            const dayStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(i).padStart(2, "0")}`;
            if (
              appointments.some(
                (appt) => formatDateToYYYYMMDD(appt.date) === dayStr,
              )
            ) {
              const matchingAppointment = appointments.find(
                (appt) => formatDateToYYYYMMDD(appt.date) === dayStr,
              );
              const marker = document.createElement("span");
              marker.classList.add("bg-primary", "rounded");
              marker.style.position = "absolute";
              marker.style.top = "0";
              marker.style.right = "0";
              marker.style.padding = "4px";
              dayElement.appendChild(marker);

              dayElement.addEventListener("click", () => {
                window.location.href = `/${userRole}/appointment-request/${matchingAppointment.id}`;
              });
            }

            // Highlight today's date
            if (
              i === currentDate.getDate() &&
              month === new Date().getMonth() &&
              year === new Date().getFullYear()
            ) {
              dayElement.classList.add("btn", "btn-primary", "active");
            }

            daysContainer.appendChild(dayElement);
          }

          // Fill the next month's days (if needed)
          const remainingDays = 42 - daysContainer.children.length; // 42 = 6 weeks x 7 days
          for (let i = 1; i <= remainingDays; i++) {
            const dayElement = document.createElement("button");
            dayElement.textContent = i;
            dayElement.classList.add("date", "faded");
            daysContainer.appendChild(dayElement);
          }
        }

        // Change month logic
        function changeMonth(delta) {
          currentDate.setMonth(currentDate.getMonth() + delta);
          updateCalendar();
        }

        // Event listeners for month navigation
        prevMonthButton.addEventListener("click", function () {
          changeMonth(-1);
        });

        nextMonthButton.addEventListener("click", function () {
          changeMonth(1);
        });

        // Helper function to format the date to "YYYY-MM-DD"
        function formatDateToYYYYMMDD(dateStr) {
          const date = new Date(dateStr);
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, "0"); // Month is 0-indexed
          const day = String(date.getDate()).padStart(2, "0");
          return `${year}-${month}-${day}`;
        }

        // Initial render
        fetchAndMarkAppointments(
          serverFormattedDate(currentDate),
          userUid,
          broadcastTime,
        );
      });
