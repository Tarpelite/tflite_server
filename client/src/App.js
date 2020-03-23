import React from 'react';
import logo from './logo.svg';
import './App.css';
import 'antd/dist/antd.css';
import { Layout, Row, Col } from 'antd';
import ImageBlock from './ImageBlock';
import Uploadblock from './UploadBlock';
const { Header, Footer, Sider, Content } = Layout;



function App() {
  return (
    <Layout>
      <Header >tflite upload client</Header>
      <Content>
        <Row>
          <Col></Col>
          <Col><ImageBlock /></Col>
          <Col><Uploadblock /></Col>
        </Row>
      </Content>
      
      <Footer style={{position:"sticky", bottom:"0"}}>
        <Col></Col>
        
      </Footer>
    </Layout>
  );
}

export default App;
