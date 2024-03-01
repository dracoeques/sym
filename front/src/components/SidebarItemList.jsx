import React from 'react';

class SidebarItemList extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            items: this.props.items,
            selectedItem: this.props.selectedItem,
            searchString: "",
        }
        this.handleChange = this.handleChange.bind(this);
        this.updateSearchString = this.updateSearchString.bind(this);
        this.onClickItem = this.onClickItem.bind(this);
    }

    handleChange(selectedOption) {
        console.log(`Option selected:`, selectedOption);
    };

    updateSearchString(e){
        this.setState({searchString:e.target.value});
    }
    onClickItem(item){
        //console.log("onClickItem",item);
        this.props.onClickItem(item);
    }

    renderItems(){

        let itemComponents = []

        for (const i in this.state.items){

            const item = this.state.items[i];
            
            //check for if this is the current item
            let itemClass = "list-group-item list-group-item-action";
            if (this.state.selectedItem){
                if (item.id === this.state.selectedItem.id){
                    itemClass = "list-group-item list-group-item-action active";
                }
            }

            //if we're searching add a filter
            if (this.state.searchString.length > 0){
                const searchString = this.state.searchString.toLowerCase();
                const title = item.title.toLowerCase();
                if (title.indexOf(searchString) !== -1){
                    itemComponents.push(
                        <li 
                            className={itemClass} 
                            key={item.id}
                            onClick={() => this.onClickItem(item)}
                        >
                            {item.title}
                        </li>
                    )
                }

            } else {
                itemComponents.push(
                    <li 
                        className={itemClass} 
                        key={item.id}
                        onClick={() => this.onClickItem(item)}
                    >
                        {item.title}
                    </li>
                )
            }
            
            
        }

        return (
            <div className="list-group">
                {itemComponents}
            </div>

        )

    }

    render(){

        const items = this.renderItems();

        return (
            <div>
                <input 
                    onChange={this.updateSearchString}
                    className="form-control me-sm-2" 
                    type="search" 
                    placeholder="Search"></input>
                {items}
            </div>
        );
    }

}

export default SidebarItemList;