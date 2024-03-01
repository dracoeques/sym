import React from 'react';

import Api from './api.js';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import * as d3 from "d3";



class CircleView extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            api:new Api(),
            sidebarHeight:window.innerHeight,
            
        }


        this.handleResize = this.handleResize.bind(this);

        this.drawChart = this.drawChart.bind(this);
        
    }

    componentDidMount(){
    
        window.addEventListener('resize', this.handleResize);
        // const promptInputBox = document.getElementById("promptInputBox");
        // promptInputBox.addEventListener('keypress', function(e){
        //     if (e.key === 'Enter') {
        //         console.log("Enter pressed");
        //         this.handleWebsocketSendMessage();
        //     }
        // }.bind(this));
        // this.configureWebsocket();

        // let data = {
        //     name:"topics",
        //     children:[
        //         {
        //             name:"Arts",
        //             children:[
        //                 {
        //                     name:"Art History",
        //                     prompt_id:1,
        //                     children:[
        //                         {
        //                             name:"Art History",
        //                             value:20,
        //                         }
        //                     ]
                            
        //                 },
        //                 {
        //                     name:"Art Technique",
        //                     prompt_id:2,
        //                     children:[
        //                         {
        //                             name:"Art Technique",
        //                             value:10,
        //                         }
        //                     ]
                            
        //                 },
        //                 {
        //                     name:"Art Theory",
        //                     prompt_id:3,
        //                     children:[
        //                         {
        //                             name:"Art Theory",
        //                             value:5,
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name:"Art Education",
        //                     prompt_id:3,
        //                     children:[
        //                         {
        //                             name:"Art Education",
        //                             value:6,
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name:"Art Skills",
        //                     prompt_id:3,
        //                     children:[
        //                         {
        //                             name:"Art Skills",
        //                             value:3,
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name:"Art Careers",
        //                     prompt_id:3,
        //                     children:[
        //                         {
        //                             name:"Art Careers",
        //                             value:1,
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name:"Art & Technology",
        //                     prompt_id:3,
        //                     children:[
        //                         {
        //                             name:"Art Theory",
        //                             value:2,
        //                         }
        //                     ]
        //                 }

        //             ]
        //         },
        //         {
        //             name:"animals",
        //             children:[
        //                 {
        //                     name:"dog",
        //                     prompt_id:4,
        //                     children:[
        //                         {
        //                             name:"dog",
        //                             value:10,
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name:"cat",
        //                     value:10,
        //                 },
        //                 {
        //                     name:"bird",
        //                     value:7,
        //                 }

        //             ]
        //         }
        //     ]
        // };

        this.loadCircleCategories();

        //this.drawChart2(data, 932, 932);

    }

    async loadCircleCategories(){
        try {
            const data = await this.state.api.loadCircleCategories();
            console.log('loadCircleCategories:', data);
            this.drawChart2(data, 932, 932);
        } catch (error) {
            console.error('Error loadCircleCategories:', error);
            this.setState({"error":error.response.data.Message});
        }
    }

    handleClick(e){
        console.log("handleClick", e);
    }


    drawChart2(data, width, height){

        const colors1 = ["hsl(152,80%,80%)", "hsl(228,30%,40%)"];
        const colors2 = ["hsl(278, 68%, 50%)", "hsl(350, 68%, 50%)"];
        const colors3 = ["hsl(202, 68%, 50%)", "hsl(233, 68%, 50%)"];
        const colors4 = ["hsl(179, 92%, 78%)", "hsl(189, 30%, 40%)"];

        let pack = data => d3.pack()
            .size([width, height])
            .padding(3)
        (d3.hierarchy(data)
            .sum(d => d.value)
            .sort((a, b) => b.value - a.value))

        const root = pack(data, width, height);
        let focus = root;
        let view;


        const color = d3.scaleLinear()
            .domain([0, 5])
            .range(colors4)
            .interpolate(d3.interpolateHcl)

        const svg = d3.select("#d3chart")
            .append("svg")
            .attr("viewBox", `-${width / 2} -${height / 2} ${width} ${height}`)
            .style("display", "block")
            .style("margin", "0 -14px")
            .style("background", color(0))
            .style("cursor", "pointer")
            .on("click", function(event) {
                console.log("click", event);
                zoom(event, root)
            });
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(root.descendants().slice(1))
            .join("circle")
            .attr("fill", d => d.children ? color(d.depth) : "white")
            .attr("pointer-events", d => !d.children ? "none" : null)
            .on("mouseover", function() { d3.select(this).attr("stroke", "#000"); })
            .on("mouseout", function() { d3.select(this).attr("stroke", null); })
            .on("click", function(event, d){
                console.log("click2", d, focus, focus !== d );
                if (focus === d ){
                    console.log("Clicked on:: ", d.data.name, d.data.prompt_id);
                    event.stopPropagation()
                    if (d.data.url){
                        window.location.href = d.data.url; //`/app/promptview/${d.data.prompt_id}`;
                    }

                    

                } else {
                    
                    zoom(event, d)
                    event.stopPropagation()
                }
                //focus !== d && (zoom(event, d), event.stopPropagation())
            });

        const label = svg.append("g")
            .style("font", "10px sans-serif")
            .attr("pointer-events", "none")
            .attr("text-anchor", "middle")
          .selectAll("text")
          .data(root.descendants())
          .join("text")
            .style("fill-opacity", d => d.parent === root ? 1 : 0)
            .style("display", d => d.parent === root ? "inline" : "none")
            .text(d => d.data.name);
        
        zoomTo([root.x, root.y, root.r * 2]);

        function zoomTo(v) {
            const k = width / v[2];

            view = v;

            label.attr("transform", d => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
            node.attr("transform", d => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
            node.attr("r", d => d.r * k);
        }

        function zoom(event, d) {
            const focus0 = focus;

            console.log("zooming to", d);
            if (!d.children){
                console.log("Stopping zoom");
                event.stopPropagation();

                console.log("Clicked on 3:: ", d.data.name, d.data.prompt_id);

                return
            }

            focus = d;

            const transition = svg.transition()
                .duration(event.altKey ? 7500 : 750)
                .tween("zoom", d => {
                const i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 4]);
                return t => zoomTo(i(t));
                });

            label
            .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
            .transition(transition)
                .style("fill-opacity", d => d.parent === focus ? 1 : 0)
                .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
                .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });
        }

        const format = d3.format(",d");

    }

    drawChart(){
        console.log("drawChart");
        const data = [12, 5, 6, 6, 9, 10];
   

        const svg = d3.select("#d3chart")
                    .append("svg")
                    .attr("width", 700)
                    .attr("height", 300);

        svg.selectAll("rect")
            .data(data)
            .enter()
            .append("rect")
            .attr("x", (d, i) => i * 70)
            .attr("y", (d, i) => 300 - 10 * d)
            .attr("width", 65)
            .attr("height", (d, i) => d * 10)
            .attr("fill", "green");

    }

    handleResize(){
        
        const innerHeight = window.innerHeight;
        console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }


    render(){



        const routerParams = this.props.params;
        
        //console.log(routerParams);
        //console.log(this.state.prompt);

        

        return (
            <div className='container-fluid'>
                <div className='row'>
                    
                    <div className='col-sm-12 bg-dark nomargin'>

                        <div
                        
                            style={{
                                height:this.state.sidebarHeight,
                                overflowY:"scroll",
                            }}
                        >
                           
                           
                            <div id="d3chart"></div>
                        </div>
                        



                    </div>
                </div>
                
            </div>
        )
    }

}

export default withRouter(CircleView);