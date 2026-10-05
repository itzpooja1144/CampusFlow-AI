document.addEventListener("DOMContentLoaded", function () {
	const searchInput = document.querySelector(".search-box input");
	const facilityCards = Array.from(document.querySelectorAll("[data-facility-name]"));

	if (!searchInput || !facilityCards.length) {
		return;
	}

	let highlightTimer;

	function showSearchMessage(message) {
		let status = document.querySelector(".search-status");

		if (!status) {
			status = document.createElement("small");
			status.className = "search-status";
			status.style.display = "block";
			status.style.marginTop = "5px";
			status.style.color = "#fb7185";
			searchInput.closest(".search-box").after(status);
		}

		status.textContent = message;
		clearTimeout(status.timer);
		status.timer = setTimeout(function () {
			status.textContent = "";
		}, 3000);
	}

	searchInput.addEventListener("keydown", function (event) {
		if (event.key !== "Enter") {
			return;
		}

		event.preventDefault();
		const query = searchInput.value.trim().toLowerCase();
		const match = facilityCards.find(function (card) {
			return card.dataset.facilityName.toLowerCase().includes(query);
		});

		if (!query || !match) {
			showSearchMessage("No matching facility found.");
			return;
		}

		const status = document.querySelector(".search-status");
		if (status) {
			status.textContent = "";
		}

		clearTimeout(highlightTimer);
		match.scrollIntoView({ behavior: "smooth", block: "center" });
		match.style.boxShadow = "0 0 0 2px #38bdf8, 0 0 24px rgba(56, 189, 248, 0.55)";

		highlightTimer = setTimeout(function () {
			match.style.boxShadow = "";
		}, 3000);
	});
});
