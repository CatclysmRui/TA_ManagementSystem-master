//ta list drag event
function moveOption(e1, e2) {
    try {
        for (let i = 0; i < e1.options.length; i++) {
            if (e1.options[i].selected) {
                var e = e1.options[i];
                e2.options.add(new Option(e.text, e.value));
                e1.remove(i);
                i = i - 1;
            }
        }
        document.ta.ranking.value = getvalue(document.ta.list2);
    } catch (e) {
    }
}

function getvalue(geto) {
    let allvalue = "";
    for (let i = 0; i < geto.options.length; i++) {
        allvalue += geto.options[i].value + ",";
    }
    return allvalue;
}

function changepos(obj, index) {
    if (index === -1) {
        if (obj.selectedIndex > 0) {
            let now = obj.options[obj.selectedIndex];
            let former = obj.options[obj.selectedIndex - 1];
            obj.insertBefore(now, former);
        }
    } else if (index === 1) {
        if (obj.selectedIndex < obj.options.length - 1) {
            let now = obj.options[obj.selectedIndex];
            let letter = obj.options[obj.selectedIndex + 1];
            obj.insertBefore(letter, now);
        }
    }
}

function showCV(e) {
    for (let i = 0; i < e.options.length; i++) {
        if (e.options[i].selected) {
            let e_selected = e.options[i];
            let name = e_selected.id;
            let link = '<a href=' + name + '>link</a>';
            $('#link').empty().append(link);
        }
    }
}

// course list drag event
function moveCourseOption(e1, e2) {
    try {
        for (let i = 0; i < e1.options.length; i++) {
            if (e1.options[i].selected) {
                var e = e1.options[i];
                e2.options.add(new Option(e.text, e.value));
                e1.remove(i);
                i = i - 1;
            }
        }
        document.course.ranking.value = getvalue(document.course.list2);
    } catch (e) {

    }
}

function showTADuty(e) {
    for (let i = 0; i < e.options.length; i++) {
        if (e.options[i].selected) {
            let e_selected = e.options[i];
            let value = e_selected.value;
            $.ajax({
                url: "ta_duty/" + value + "/", //the endpoint
                type: "GET", // http method
                dataType: "json",
                //handle a successful response
                success: function (data) {
                    console.log("success");
                    let trHTML = '';
                    trHTML += '<table border="2" bordercolor="black" width="300" height="100" cellspacing="0" cellpadding="5">' +
                        '<tr>\n' +
                        '            <th>classification</th>\n' +
                        '            <th>times</th>\n' +
                        '            <th>teaching activity</th>\n' +
                        '            <th>Approx. hours/student</th>\n' +
                        '        </tr>';
                    trHTML += '<tr>\n' +
                        '            <td rowspan="3">Lab</td>\n' +
                        '            <td rowspan="3">' + data["labNumber"] + '</td>\n' +
                        '            <td>preparation</td>\n' +
                        '            <td>' + data["preparationHour"] + '</td>\n' +
                        '        </tr>';
                    trHTML += '<tr>\n' +
                        '            <td>lab time</td>\n' +
                        '            <td>' + data["labHour"] + '</td>\n' +
                        '        </tr>\n' +
                        '        <tr>\n' +
                        '            <td>working</td>\n' +
                        '            <td>' + data["labWorkingHour"] + '</td>\n' +
                        '        </tr>\n' +
                        '        <tr>\n' +
                        '            <td>Assignment</td>\n' +
                        '            <td>' + data["assignmentNumber"] + '</td>\n' +
                        '            <td>working</td>\n' +
                        '            <td>' + data["assignmentWorkingHour"] + '</td>\n' +
                        '        </tr>';
                    trHTML += '<tr>\n' +
                        '            <td rowspan="2">Others</td>\n' +
                        '            <td rowspan="2"></td>\n' +
                        '            <td>contact hour</td>\n' +
                        '            <td>' + data["contactHour"] + '</td>\n' +
                        '        </tr>\n' +
                        '        <tr>\n' +
                        '            <td>other duties</td>\n' +
                        '            <td>' + data["otherDutiesHour"] + '</td>\n' +
                        '        </tr>' +
                        '</table>';
                    trHTML += '<p>total hour:'+data['totalHour']+' </p>';
                    trHTML += '<p>ta positions:'+data['recommendedTANumber']+'</p>';

                    let duty = "<p>TA duties/detail</p>";

                    $('#taduty').empty().append(duty, trHTML);
                },

                // handel a unsuccessful response
                error: function () {
                    console.log("error!")
                }
            })
        }
    }
}


function setStatus() {
    try {
        let select = document.getElementsByClassName('select-option');
        for (let i = 0; i < select.length; i++) {
            let value = select[i].options[select[i].selectedIndex].value;
            let status = value.split('-');
            if (status[1] === 'rejected') {
                let state = document.getElementById('statusResult').value;
                let send = state.split(',');
                if (send.includes(status[0]) === false) {
                    document.resultForm.status.value += status[0] + ',';
                }
            } else if (status[1] === 'approved') {
                let value = document.getElementById('statusResult').value;
                if (value.includes(status[0]) === true) {
                    document.resultForm.status.value = value.replace(status[0] + ',', '');
                }
            }
        }
    } catch (e) {
    }

}

function floatWindow(id) {
    document.getElementById('light').style.display = 'block';
    document.getElementById('fade').style.display = 'block';
    $.ajax({
        url: "duty/" + id, //the endpoint
        type: "GET", // http method
        //handle a successful response
        success: function (data) {
            let trHTML = '';
            trHTML += '<table>' +
                '<tr>\n' +
                '            <th>classification</th>\n' +
                '            <th>times</th>\n' +
                '            <th>teaching activity</th>\n' +
                '            <th>Approx. hours/student</th>\n' +
                '        </tr>';

            trHTML += '<tr>\n' +
                '            <td rowspan="3">Lab</td>\n' +
                '            <td rowspan="3">' + data["labNumber"] + '</td>\n' +
                '            <td>preparation</td>\n' +
                '            <td>' + data["preparationHour"] + '</td>\n' +
                '        </tr>';

            trHTML += '<tr>\n' +
                '            <td>lab time</td>\n' +
                '            <td>' + data["labHour"] + '</td>\n' +
                '        </tr>\n' +
                '        <tr>\n' +
                '            <td>working</td>\n' +
                '            <td>' + data["labWorkingHour"] + '</td>\n' +
                '        </tr>\n' +
                '        <tr>\n' +
                '            <td>Assignment</td>\n' +
                '            <td>' + data["assignmentNumber"] + '</td>\n' +
                '            <td>working</td>\n' +
                '            <td>' + data["assignmentWorkingHour"] + '</td>\n' +
                '        </tr>';
            trHTML += '<tr>\n' +
                '            <td rowspan="2">Others</td>\n' +
                '            <td rowspan="2"></td>\n' +
                '            <td>contact hour</td>\n' +
                '            <td>' + data["contactHour"] + '</td>\n' +
                '        </tr>\n' +
                '        <tr>\n' +
                '            <td>other duties</td>\n' +
                '            <td>' + data["otherDutiesHour"] + '</td>\n' +
                '        </tr>' +
                '</table>';
            trHTML += '<p>total hour:'+data['totalHour']+' </p>';
            trHTML += '<p>ta positions:'+data['recommendedTANumber']+'</p>';
            $('#insert').empty().append(trHTML);
        },
        // handel a unsuccessful response
        error: function () {
            console.log("error!")
        }
    })
}

function closeItem() {
    document.getElementById('light').style.display = 'none';
    document.getElementById('fade').style.display = 'none';
}

function editable(id, editID, saveID) {
    let edit = document.getElementById(id);
    edit.setAttribute('contenteditable', true);
    document.getElementById(editID).style.display = 'none';
    document.getElementById(saveID).style.display = 'inline';
}

function cancel(positions, id, editID, saveID) {
    document.getElementById(id).innerHTML = positions;
    document.getElementById(id).setAttribute('contenteditable', false);
    document.getElementById(editID).style.display = 'inline';
    document.getElementById(saveID).style.display = 'none';
}

function save(id, editID, saveID) {
    let positions = document.getElementById(id).innerText;
    console.log(positions);
    $.ajax({
        url: "save/",
        type: "POST",
        data: {"positions": positions, "id": id},
        dataType: 'json',
        success: function (textStatus) {
            console.log('success');
            cancel(positions,id,editID,saveID);
        },
        error: function () {
            console.log('error!');
        },
    });
}