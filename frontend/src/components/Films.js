import * as React from 'react';
import Sidebar from "./Sidebar"
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import axios from "axios"

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';

import FilmIcon from "../images/video_camera.png"

import "../css/index.css"

export default function Films() {
    const [value, setValue] = React.useState('1');
    const [films, setFilms] = React.useState([]);

    const [recPrefFilms, setRecPrefFilms] = React.useState([]);
    const [recLikedFilms, setRecLikedFilms] = React.useState([]);
    const [recWtchFilms, setRecWtchFilms] = React.useState([]);
    const [recFilms, setRecFilms] = React.useState([]);

    function handleUnlike(title) {
        console.log(title)
        console.log(localStorage.getItem("email"))
        axios.post("http://localhost:5000/unlikefilm", {}, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleLike(title) {
        console.log(title)
        console.log(localStorage.getItem("email"))
        axios.post("http://localhost:5000/likefilm", {}, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleWatch(title) {
        axios.post("http://localhost:5000/watchfilm", null, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleIgnore(title) {
        axios.post("http://localhost:5000/ignorerecommandation", null, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleLikeTab3(title) {
        console.log(title)
        console.log(localStorage.getItem("email"))
        axios.post("http://localhost:5000/likerblfilm", {}, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleLikeTab4(title) {
        console.log(title)
        console.log(localStorage.getItem("email"))
        axios.post("http://localhost:5000/likerbwfilm", {}, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    function handleLikeTab5(title) {
        console.log(title)
        console.log(localStorage.getItem("email"))
        axios.post("http://localhost:5000/likerballfilm", {}, {
            params: {
                email: localStorage.getItem("email"),
                film: title
            }
        })
            .then(res => {
                console.log(res);
            })
            .catch(err => {
                console.log(err);
            });
    }

    const handleChange = (event, newValue) => {
        setValue(newValue);
        if (newValue == 1) {
            axios.get("http://localhost:5000/getallfilms")
                .then(res => {
                    console.log(res.data.films);
                    setFilms(res.data.films)
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 2) {
            axios.get("http://localhost:5000/getuserrecommendedbasedonmoviespreffered", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setRecPrefFilms(res.data.films);
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 3) {
            axios.get("http://localhost:5000/getuserrecommendedbasedonmoviesliked", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setRecLikedFilms(res.data.films);
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 4) {
            axios.get("http://localhost:5000/getuserrecommendedbasedonmovieswatched", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setRecWtchFilms(res.data.films);
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 5) {
            axios.get("http://localhost:5000/getuserrecommendedfilms3factors", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setRecFilms(res.data.films);
                })
                .catch(err => {
                    console.log(err);
                });
        }
    };
    return (
        <>
            <Sidebar style={{ position: 'absolute' }}></Sidebar>
            <Box sx={{ width: '100%', typography: 'body1', marginLeft: "200px", paddingRight: "400px", paddingTop: "50px" }}>
                <TabContext value={value}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <TabList onChange={handleChange} aria-label="lab API tabs example">
                            <Tab style={{color:"#adbac7"}} label="Films" value="1" />
                            <Tab style={{color:"#adbac7"}} label="Recommended films based on prefferences" value="2" />
                            <Tab style={{color:"#adbac7"}} label="Recommended films based on liked ones" value="3" />
                            <Tab style={{color:"#adbac7"}} label="Recommended films based on watched films" value="4" />
                            <Tab style={{color:"#adbac7"}} label="Recommended films based on all three metrics" value="5" />
                        </TabList>
                    </Box>
                    <TabPanel value="1">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Title</TableCell>
                                        <TableCell align="right">Genres</TableCell>
                                        <TableCell align="right">Realease date</TableCell>
                                        <TableCell align="right">Budget</TableCell>
                                        <TableCell align="right">Runtime</TableCell>
                                        <TableCell align="right">Popularity</TableCell>
                                        <TableCell align="right">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {films.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.original_title}
                                            </TableCell>
                                            <TableCell align="right">{item.genres}</TableCell>
                                            <TableCell align="right">{item.release_date}</TableCell>
                                            <TableCell align="right">{item.budget}</TableCell>
                                            <TableCell align="right">{item.runtime}</TableCell>
                                            <TableCell align="right">{item.popularity}</TableCell>
                                            <TableCell align="right">
                                                <Button color="inherit" style={{ backgroundColor: "#106cdc", marginBottom:"5px" }} onClick={() => handleLike(item.original_title)}><b>Like</b></Button><br></br>
                                                <Button color="inherit" style={{ backgroundColor: "coral", marginBottom:"5px" }} onClick={() => handleIgnore(item.original_title)}><b>Ignore</b></Button><br></br>
                                                <Button color="inherit" style={{ backgroundColor: "#2ca460", width:"20px" }} onClick={() => handleWatch(item.original_title)}><b>Watch</b></Button>
                                                {/* <Button color="inherit" style={{ backgroundColor: "orange" }} onClick={() => handleUnlike(item.original_title)}>Unlike</Button> */}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>
                    <TabPanel value="2">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Title</TableCell>
                                        <TableCell align="right">Genres</TableCell>
                                        <TableCell align="right">Realease date</TableCell>
                                        <TableCell align="right">Budget</TableCell>
                                        <TableCell align="right">Runtime</TableCell>
                                        <TableCell align="right">Popularity</TableCell>
                                        <TableCell align="right">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {recPrefFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.original_title}
                                            </TableCell>
                                            <TableCell align="right">{item.genres}</TableCell>
                                            <TableCell align="right">{item.release_date}</TableCell>
                                            <TableCell align="right">{item.budget}</TableCell>
                                            <TableCell align="right">{item.runtime}</TableCell>
                                            <TableCell align="right">{item.popularity}</TableCell>
                                            <TableCell align="right">
                                                <Button color="inherit" style={{ backgroundColor: "#106cdc", marginRight:"5px" }} onClick={() => handleLike(item.original_title)}><b>Like</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "coral", marginRight:"5px" }} onClick={() => handleIgnore(item.original_title)}><b>Ignore</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "#2ca460" }} onClick={() => handleWatch(item.original_title)}><b>Watch</b></Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>
                    <TabPanel value="3">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Title</TableCell>
                                        <TableCell align="right">Genres</TableCell>
                                        <TableCell align="right">Realease date</TableCell>
                                        <TableCell align="right">Budget</TableCell>
                                        <TableCell align="right">Runtime</TableCell>
                                        <TableCell align="right">Popularity</TableCell>
                                        <TableCell align="right">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {recLikedFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.original_title}
                                            </TableCell>
                                            <TableCell align="right">{item.genres}</TableCell>
                                            <TableCell align="right">{item.release_date}</TableCell>
                                            <TableCell align="right">{item.budget}</TableCell>
                                            <TableCell align="right">{item.runtime}</TableCell>
                                            <TableCell align="right">{item.popularity}</TableCell>
                                            <TableCell align="right">
                                                <Button color="inherit" style={{ backgroundColor: "#106cdc", marginRight:"5px" }} onClick={() => handleLikeTab3(item.original_title)}><b>Like</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "coral", marginRight:"5px" }} onClick={() => handleIgnore(item.original_title)}><b>Ignore</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "#2ca460" }} onClick={() => handleWatch(item.original_title)}><b>Watch</b></Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>
                    <TabPanel value="4">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Title</TableCell>
                                        <TableCell align="right">Genres</TableCell>
                                        <TableCell align="right">Realease date</TableCell>
                                        <TableCell align="right">Budget</TableCell>
                                        <TableCell align="right">Runtime</TableCell>
                                        <TableCell align="right">Popularity</TableCell>
                                        <TableCell align="right">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {recWtchFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.original_title}
                                            </TableCell>
                                            <TableCell align="right">{item.genres}</TableCell>
                                            <TableCell align="right">{item.release_date}</TableCell>
                                            <TableCell align="right">{item.budget}</TableCell>
                                            <TableCell align="right">{item.runtime}</TableCell>
                                            <TableCell align="right">{item.popularity}</TableCell>
                                            <TableCell align="right">
                                                <Button color="inherit" style={{ backgroundColor: "#106cdc", marginRight:"5px" }} onClick={() => handleLikeTab4(item.original_title)}><b>Like</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "coral", marginRight:"5px" }} onClick={() => handleIgnore(item.original_title)}><b>Ignore</b></Button>
                                                <Button color="inherit" style={{ backgroundColor: "#2ca460" }} onClick={() => handleWatch(item.original_title)}><b>Watch</b></Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>
                    <TabPanel value="5">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Title</TableCell>
                                        <TableCell align="right">Genres</TableCell>
                                        <TableCell align="right">Realease date</TableCell>
                                        <TableCell align="right">Budget</TableCell>
                                        <TableCell align="right">Runtime</TableCell>
                                        <TableCell align="right">Popularity</TableCell>
                                        <TableCell align="right">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {recFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.original_title}
                                            </TableCell>
                                            <TableCell align="right">{item.genres}</TableCell>
                                            <TableCell align="right">{item.release_date}</TableCell>
                                            <TableCell align="right">{item.budget}</TableCell>
                                            <TableCell align="right">{item.runtime}</TableCell>
                                            <TableCell align="right">{item.popularity}</TableCell>
                                            <TableCell align="right">
                                                <Button color="inherit" style={{ backgroundColor: "#106cdc", marginBottom:"5px" }} onClick={() => handleLikeTab5(item.original_title)}><b>Like</b></Button><br></br>
                                                <Button color="inherit" style={{ backgroundColor: "coral", marginBottom:"5px" }} onClick={() => handleIgnore(item.original_title)}><b>Ignore</b></Button><br></br>
                                                <Button color="inherit" style={{ backgroundColor: "#2ca460" }} onClick={() => handleWatch(item.original_title)}><b>Watch</b></Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>
                </TabContext>
            </Box>
        </>
    )
}
