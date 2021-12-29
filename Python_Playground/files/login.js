// I suck at server side code, luckily I know how to make things secure without it - Connor
function string_to_int_array(str) {
    const intArr = [];

    for (let i = 0; i < str.length; i++) {
        const charcode = str.charCodeAt(i);

        const partA = Math.floor(charcode / 26);
        const partB = charcode % 26;

        intArr.push(partA);
        intArr.push(partB);
    }

    return intArr;
}

function int_array_to_text(int_array) {
    let txt = '';

    for (let i = 0; i < int_array.length; i++) {
        txt += String.fromCharCode(97 + int_array[i]);
    }

    return txt;
}

document.forms[0].onsubmit = function(e) {
    e.preventDefault();

    if (document.getElementById('username').value !== 'connor') {
        document.getElementById('fail').style.display = '';
        return false;
    }

    const chosenPass = document.getElementById('inputPassword').value;

    const hash = int_array_to_text(string_to_int_array(int_array_to_text(string_to_int_array(chosenPass))));

    if (hash === 'dxeedxebdwemdwesdxdtdweqdxefdxefdxdudueqduerdvdtdvdu') {
        window.location = 'super-secret-admin-testing-panel.html';
    } else {
        document.getElementById('fail').style.display = '';
    }
    return false;
}