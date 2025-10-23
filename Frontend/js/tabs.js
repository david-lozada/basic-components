let tabs = document.querySelectorAll('.tab-button');

tabs.forEach(tab => {
	tab.addEventListener('click', () => {
		let target = tab.getAttribute('data-tab');
		// Deactivate all tabs and contents
		tabs.forEach(t => t.classList.remove('active'));
		document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('visible'));

		// Activate the clicked tab and corresponding content
		tab.classList.add('active');
		document.getElementById(target).classList.add('visible');
	});
});