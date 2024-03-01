import React, { Component } from 'react';
import Api from './api.js';

class CircleComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      api:new Api(),
      isZoomed: false,
      radius:50,
      largeSphereRadius: 250, 
      svgWidth: 800,
      svgHeight: 800,
      showInnerTextArea: false, //set to true to enable text
    };

    this.drawChart = this.drawChart.bind(this);
    this.zoomIn = this.zoomIn.bind(this);
    this.clickInner = this.clickInner.bind(this);
  }

  componentDidMount(){
    this.loadCircleCategories();
  }

  async loadCircleCategories(){
    try {
        const data = await this.state.api.loadArchetypeCategories();
        console.log('loadArchetypeCategories:', data);
        this.drawChart(data, this.state.svgWidth, this.state.svgHeight);
    } catch (error) {
        console.error('Error loadArchetypeCategories:', error);
        this.setState({"error":error.response.data.Message});
    }
  }

  drawChart(data, width, height){
    console.log(data, width, height);

    const categories = data;
    const svg = document.getElementById('main-svg');
    const centerX = 400, centerY = 400, largeRadius = 250, smallRadius = 70;
    let circleCounter = 0;

    for (let i = 0; i < 7; i++) {

      const category = categories[i]

      const angle1 = (2 * Math.PI / 7) * i;
      const largeX = centerX + largeRadius * Math.cos(angle1);
      const largeY = centerY + largeRadius * Math.sin(angle1);
      const largeCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      largeCircle.setAttribute('cx', largeX);
      largeCircle.setAttribute('cy', largeY);
      largeCircle.setAttribute('r', smallRadius);
      largeCircle.setAttribute('class', 'inner-sphere');
      largeCircle.setAttribute('dcx', largeX);
      largeCircle.setAttribute('dcy', largeY);
      largeCircle.setAttribute('dr', smallRadius);
      svg.appendChild(largeCircle);
      
      const largeLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      largeLabel.setAttribute('x', largeX);
      largeLabel.setAttribute('y', largeY);
      largeLabel.setAttribute('text-anchor', 'middle');
      largeLabel.setAttribute('dy', '.3em');
      largeLabel.textContent =  category.name; //`L${i + 1}`;
      largeLabel.setAttribute('class', 'inner-text');
      largeLabel.setAttribute('dcx', largeX);
      largeLabel.setAttribute('dcy', largeY);
      largeLabel.setAttribute('dr', smallRadius);
      svg.appendChild(largeLabel);

      for (let j = 0; j < 7; j++) {
        const subcategory = categories[i].children[j];

        circleCounter++;
        const angle2 = (2 * Math.PI / 7) * j;
        const x = largeX + smallRadius * Math.cos(angle2);
        const y = largeY + smallRadius * Math.sin(angle2);
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', smallRadius / 3);
        circle.setAttribute('dcx', x);
        circle.setAttribute('dcy', y);
        circle.setAttribute('dr', smallRadius);
        circle.setAttribute('parent', largeCircle);
        circle.setAttribute('class', 'inner-sphere-small');
        circle.setAttribute('url', subcategory.url);
        svg.appendChild(circle);

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', x);
        label.setAttribute('y', y);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('dy', '.3em');
        label.textContent = subcategory.name//`S${circleCounter}`;
        label.setAttribute('dcx', x);
        label.setAttribute('dcy', y);
        label.setAttribute('parent', largeCircle);
        label.setAttribute('dr', smallRadius );
        label.setAttribute('url', subcategory.url);
        //label.setAttribute('class', 'inner-text');

        label.setAttribute('class', 'inner-text-small');
        svg.appendChild(label);
      }
    }

      const innerSpheres = document.querySelectorAll('.inner-sphere');
      innerSpheres.forEach(circle => circle.addEventListener('click', this.zoomIn));
      
      const innerTexts = document.querySelectorAll('.inner-text');
      innerTexts.forEach(text => text.addEventListener('click', this.zoomIn));


      const innerSpheresSmall = document.querySelectorAll('.inner-sphere-small');
      innerSpheresSmall.forEach(circle => {
        circle.addEventListener('click', this.clickInner)
        circle.dataset.originalRadius = circle.getAttribute('r');
         // Attach hover-in (mouseover) and hover-out (mouseout) event listeners
         circle.addEventListener('mouseover', function() {
            //const originalRadius = parseFloat(circle.dataset.originalRadius);
            //circle.setAttribute('r', originalRadius * 1.2); // Increase the radius by 20%
        });

        circle.addEventListener('mouseout', function() {
            //circle.setAttribute('r', circle.dataset.originalRadius); // Reset the radius
        });
      });
      
      const innerTextsSmall = document.querySelectorAll('.inner-text-small');
      innerTextsSmall.forEach(text => text.addEventListener('click', this.clickInner));


  }

  handleMouseOver = () => {
    this.setState({
      radius: this.state.radius * 1.2
    });
  }

  handleMouseOut = () => {
    this.setState({
      radius: this.state.radius / 1.2
    });
  }

  handleZoom = () => {
    const isZoomed = this.state.isZoomed;
    // Assuming you're using a viewBox to zoom. Adjust accordingly.
    const svg = document.getElementById('main-svg');
    if (isZoomed) {
      svg.setAttribute('viewBox', '0 0 600 600');
    } else {
      // Example zoom, adjust to your needs
      svg.setAttribute('viewBox', '150 150 300 300');
    }

    this.setState({
      isZoomed: !isZoomed
    });
  }

  zoomIn(evt, target) {

    //console.log("zoom", x);

    const isZoomed = this.state.isZoomed;

    const svg = document.getElementById('main-svg');
    let circleElement = evt.target;
    if (target){
      //optionally we can manually trigger zoom and set target
      circleElement = target;
    }
    
    const cx = parseFloat(circleElement.getAttribute('dcx'));
    const cy = parseFloat(circleElement.getAttribute('dcy'));
    const r = parseFloat(circleElement.getAttribute('dr'));

    let startViewBox, endViewBox;

    const zoomScale = 3.5;
    const offsetScale = 2;
    const xOffset = 100;
    const yOffset = 100;

    if (!isZoomed) {
        startViewBox = { x: 0, y: 0, width: 800, height: 800 };
        endViewBox = { x: cx - r*offsetScale, y: cy - r*offsetScale, width: r * zoomScale, height: r * zoomScale };

        
        let element = document.querySelector('#center-input'); // Select the element by its ID
        element.setAttribute('hidden', true); // This will hide the element
    } else {
        startViewBox = { x: cx - r*offsetScale, y: cy - r*offsetScale, width: r * zoomScale, height: r * zoomScale };
        endViewBox = { x: 0, y: 0, width: 800, height: 800 };

       
    }
    
    const duration = 300; // Animation duration in milliseconds
    const stepCount = 30; // Number of animation steps
    let currentStep = 0;

    function easeInOutCubic(t) {
        if (t < 0.5) {
            return 4 * t * t * t;
        } else {
            return 1 - Math.pow(-2 * t + 2, 3) / 2;
        }
    }

    function linearZoom(t) {
        return t
    }

    // Animate the viewBox values
    const animateViewBox = () => {
        currentStep++;
        let progress = currentStep / stepCount;
        progress = easeInOutCubic(progress);
        const newViewBox = {
            x: startViewBox.x + (endViewBox.x - startViewBox.x) * progress,
            y: startViewBox.y + (endViewBox.y - startViewBox.y) * progress,
            width: startViewBox.width + (endViewBox.width - startViewBox.width) * progress,
            height: startViewBox.height + (endViewBox.height - startViewBox.height) * progress,
        };
        svg.setAttribute('viewBox', `${newViewBox.x} ${newViewBox.y} ${newViewBox.width} ${newViewBox.height}`);
        
        if (currentStep < stepCount) {
            requestAnimationFrame(animateViewBox);
        } else {
            
            if (isZoomed){
              let element = document.querySelector('#center-input'); // Select the element by its ID
              element.removeAttribute('hidden'); // This will show the element

            }
            this.setState({isZoomed: !isZoomed})
        }
    };

    // Start the animation
    animateViewBox();
  }

  //click an inner circle
  clickInner(evt) {
    const isZoomed = this.state.isZoomed;
    if (!isZoomed) {
        //do nothing
        //zoom to the parent
        console.log("inner zoom");
        
        const c = evt.target.getAttribute('parent')
        console.log(c);
        
        this.zoomIn(evt, c);
    } else {
        const circleElement = evt.target;
        //console.log("clickInner", circleElement);
        const url = circleElement.getAttribute("url");
        window.location.href = url;
    }
  }

  render() {
    const { radius } = this.state;

    let inner_text = (<div id="center-input"></div>);
    if (this.state.showInnerTextArea){
      inner_text = (<input id="center-input" type="text" className="form-control bg-primary chat-input text-light centered-input" placeholder="Enter text here" />);

    }

    return (
      <div style={{backgroundColor: "#57375d", height: window.innerHeight}}>
      <div className="svg-container" style={{margin:"0 auto"}}>
    
      {inner_text}

      <svg id="main-svg" width="800" height="800" viewBox="0 0 800 800" >
        <circle className="outer-sphere" cx="400" cy="400" r="250"  />
      </svg>
    </div>
    </div>
    );
  }
}

export default CircleComponent;
