import {Card} from 'antd';
import React from 'react';

const {Meta} = Card;

class ImageBlock extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            class1:"",
            class2:"",
            class3:"",
            result:""
        }
    }
    componentWillMount(){

        fetch("http://123.57.0.181:5000/score/")
        .then(res=>res.json())
        .then(
            (result) =>{
                console.log(result);
                this.setState({
                    class1:result.wire_opening,
                    class2:result.nest,
                    class3:result.grass,
                    result:result.result
                });
            }
        )


    }

    render(){return(
        <Card hoverable
            style={{width:240}}
            cover={<img alt="example" src="http://123.57.0.181:5000/handle_image/" />}>
        
        <Meta title={this.state.result} descroption={this.state.class1}></Meta>

        </Card>
    )
    }
}

export default ImageBlock;