import {Upload, message, Button} from 'antd';
import {UploadOutlined} from '@ant-design/icons';
import React from 'react';

class Uploadblock extends React.Component {
    state = {
      fileList: [],
      uploading: false,
    };
  
    handleUpload = () => {
      const { fileList } = this.state;
      const formData = new FormData();
      formData.append('file', fileList[0]);
    //   fileList.forEach(file => {
    //     formData.append('file', file);
    //   });
  
      this.setState({
        uploading: true,
      });
  
      // You can use any AJAX library you like
      var requestOptions = {
        method: 'POST',
        body: formData,
        redirect: 'follow'
      };

      fetch("http://123.57.0.181:5000/handle_image/", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result), this.setState({uploading:false}, alert("upload successfully!")))
        .catch(error => console.log('error', error));

    //   fetch({
    //     url: '123.57.0.181:5000/handle_image/',
    //     method: 'post',
    //     processData: false,
    //     data: formData,
    //     success: () => {
    //       this.setState({
    //         fileList: [],
    //         uploading: false,
    //       });
    //       message.success('upload successfully.');
    //     },
    //     error: () => {
    //       this.setState({
    //         uploading: false,
    //       });
    //       message.error('upload failed.');
    //     },
    //   });
    };
  
    render() {
      const { uploading, fileList } = this.state;
      const props = {
        onRemove: file => {
          this.setState(state => {
            const index = state.fileList.indexOf(file);
            const newFileList = state.fileList.slice();
            newFileList.splice(index, 1);
            return {
              fileList: newFileList,
            };
          });
        },
        beforeUpload: file => {
          this.setState(state => ({
            fileList: [...state.fileList, file],
          }));
          return false;
        },
        fileList,
      };
  
      return (
        <div>
          <Upload {...props}>
            <Button>
              <UploadOutlined /> Select File
            </Button>
          </Upload>
          <Button
            type="primary"
            onClick={this.handleUpload}
            disabled={fileList.length === 0}
            loading={uploading}
            style={{ marginTop: 16 }}
          >
            {uploading ? 'Uploading' : 'Start Upload'}
          </Button>
        </div>
      );
    }
  }
  
  export default Uploadblock;
