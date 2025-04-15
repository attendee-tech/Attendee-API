const apiurl = "http://127.0.0.1:8000/schools";
const stddata = {
  matricule_number: "1235s",
};
fetch(apiurl, {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.log(error));

