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
import TextField from '@mui/material/TextField';

import FilmIcon from "../images/film_roll.png"

import "../css/index.css"

export default function Profile() {
    const [value, setValue] = React.useState('1');
    const [statistics, setStatistics] = React.useState([]);

    const [likedFilms, setLikedFilms] = React.useState([]);
    const [ignoredFilms, setIgnoredFilms] = React.useState([]);
    const [watchedFilms, setWatchedFilms] = React.useState([]);

    const handleChange = (event, newValue) => {
        setValue(newValue);
        if (newValue == 1) {
            axios.get("http://localhost:5000/getstatistics", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.statistics);
                    setStatistics(res.data.statistics)
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 2) {
            axios.get("http://localhost:5000/getfilmsliked", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setLikedFilms(res.data.films)
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 3) {
            axios.get("http://localhost:5000/getfilmsignored", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setIgnoredFilms(res.data.films)
                })
                .catch(err => {
                    console.log(err);
                });
        }
        if (newValue == 4) {
            axios.get("http://localhost:5000/getfilmswatched", {
                params: {
                    email: localStorage.getItem("email")
                }
            })
                .then(res => {
                    console.log(res.data.films);
                    setWatchedFilms(res.data.films)
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
                            <Tab style={{ color: "#adbac7" }} label="Statistics" value="1" />
                            <Tab style={{ color: "#adbac7" }} label="Films liked" value="2" />
                            <Tab style={{ color: "#adbac7" }} label="Films ignored" value="3" />
                            <Tab style={{ color: "#adbac7" }} label="Watched films" value="4" />
                        </TabList>
                    </Box>
                    <TabPanel value="1">
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Intralist similarity</TableCell>
                                        <TableCell align="right">Recommender system recall based on liked movies</TableCell>
                                        <TableCell align="right">Recommender system recall based on watched movies</TableCell>
                                        <TableCell align="right">Recommender system recall based on all</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {statistics.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                {item.is}
                                            </TableCell>
                                            <TableCell align="right">{item.bl}</TableCell>
                                            <TableCell align="right">{item.bw}</TableCell>
                                            <TableCell align="right">{item.ba}</TableCell>
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
                                        <TableCell>Film name</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {likedFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.name}
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
                                        <TableCell>Film name</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {ignoredFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">

                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.name}
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
                                        <TableCell>Film name</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {watchedFilms.map((item, index) => (
                                        <TableRow
                                            // key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell component="th" scope="row">
                                                <img style={{ paddingRight: "10px" }} src={FilmIcon} alt="FilmIcon" />
                                                {item.name}
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
