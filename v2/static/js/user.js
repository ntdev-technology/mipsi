
function editItem(item) {
	console.log(`edit${item}`);
	const but = document.getElementById(`but${item}`);
	const val = document.getElementById(`val${item}`);
	but.onclick = function() { saveItem(item); }
	but.innerHTML = 'Save'

	ip = document.createElement('input')
	ip.value = val.innerHTML
	ip.id = `ip${item}`
	val.innerHTML = ''
	val.appendChild(ip)
}

function saveItem(item) {
	console.log(`save${item}`);
	const but = document.getElementById(`but${item}`);
	const val = document.getElementById(`val${item}`);
	const ip  = document.getElementById(`ip${item}`);
	but.onclick = function() { editItem(item); };
	but.innerHTML = 'Edit';

	const headers = {};
	headers['item'] = item;
	headers[item] = ip.value;
	ip.remove();
	val.innerHTML = 'loading...'
	
	fetch(`/users/${user.id}`, {
		method: 'UPDATE',
		headers: headers
	}).then(res => {
		console.log(res);
		console.log('value updated');
	}).error(err => {
		console.error('fetch error', err);
	})
	
	/*val.innerHTML = ip.value;*/
}