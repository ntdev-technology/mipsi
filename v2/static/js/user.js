const selectRoles = document.getElementById('selectRoles');
const currentRoles = document.getElementById('currentRoles');
const editRolesHelp = document.getElementById('editRolesHelp');

selectRoles.addEventListener('change', () => {
    const selectedRoles = Array.from(selectRoles.selectedOptions, option => option.value);
    currentRoles.innerHTML = selectedRoles.map(role => role + '<br>').join('');
});

function editItem(item) {
	console.log(`edit${item}`);
	const but  = document.getElementById(`but${item}`);
	const val  = document.getElementById(`val${item}`);
	
	but.innerHTML = 'Save';
	but.onclick = function() { saveItem(item); };
	
	if (item === 'roles') {
        selectRoles.style.display = 'block';
		editRolesHelp.style.display = 'block';
		return
	} else {
		ip = document.createElement('input');
		ip.value = val.innerHTML;
		ip.id = `ip${item}`;
		val.innerHTML = '';
		val.appendChild(ip);
	}
}

function saveItem(item) {
	const but = document.getElementById(`but${item}`);
	const val = document.getElementById(`val${item}`);
	const ip  = document.getElementById(`ip${item}`);
	
	console.log(`save${item}`);
	
	but.onclick = function() { editItem(item); };
	but.innerHTML = 'Edit';

	const headers = {};
	headers['item'] = item;

	if (item === 'roles') {
		selectRoles.style.display = 'none';
		editRolesHelp.style.display = 'none';
		const selectedRoles = Array.from(selectRoles.selectedOptions, option => parseInt(option.value[0]));
        headers[item] = JSON.stringify(selectedRoles);
	} else {
		headers[item] = ip.value;
		ip.remove();
		val.innerHTML = 'loading...';
	}


	
	fetch(`/users/${user.id}`, {
		method: 'UPDATE',
		headers: headers
	})
	.then(res => res.json())
	.then(res => {
		if (res.item === 'roles') {
			currentRoles.innerHTML = res.value;
		} else if (res.item === 'id') {
			window.location.href = `/users/${res.value}`;
		} else {
			val.textContent = res.value;
		}
	});
}