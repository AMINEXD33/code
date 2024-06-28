import Cookies from 'js-cookie';

const END_POINT = "http://localhost:8000/api/login/";

function splite_date(dateString)
{
    let date_ = dateString.split(' ');
    let year_month = date_[0].split("/");
    let day_hour_s = date_[1].split(":");

    let year = parseInt(year_month[0]);
    let month = parseInt(year_month[1]) - 1;
    let day = parseInt(year_month[2]);
    let hour = parseInt(day_hour_s[0]);
    let minute = parseInt(day_hour_s[1]);
    let second = parseInt(day_hour_s[2]);
    let date_obj = new Date(year, month, day, hour, minute, second);
    return(date_obj);
}
function log_user_in(token)
{
    console.log(token);
    let expires_at = splite_date(token["expired_date"])

    Cookies.set("JWT", token["JWT"], {expires:expires_at})

}
export async function login(username, password)
{
    return new Promise(async(resolve, reject)=>{
        const resp = await fetch(END_POINT, 
            {
                method:"POST",
                body: JSON.stringify({
                    "username": username,
                    "password": password
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
            }
        )
        if (!resp.ok)
        {
            reject(new Error ("login failed !"));
        }
        let token = await resp.json()
        .then(data=>log_user_in(data))
        .catch(error=>console.log(error));
        console.log("here");
        resolve(true);
    })
}