package com.example.tflite_server;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;


import com.koushikdutta.async.http.AsyncHttpClient;
import com.koushikdutta.async.http.AsyncHttpPost;
import com.koushikdutta.async.http.AsyncHttpResponse;
import com.koushikdutta.async.http.body.MultipartFormDataBody;

import com.squareup.picasso.Picasso;
import com.squareup.picasso.Target;

import org.json.JSONObject;
import org.tensorflow.lite.DataType;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.common.FileUtil;
import org.tensorflow.lite.support.common.TensorOperator;
import org.tensorflow.lite.support.common.TensorProcessor;
import org.tensorflow.lite.support.common.ops.NormalizeOp;
import org.tensorflow.lite.support.image.ImageProcessor;
import org.tensorflow.lite.support.image.TensorImage;
import org.tensorflow.lite.support.image.ops.ResizeOp;
import org.tensorflow.lite.support.image.ops.ResizeOp.ResizeMethod;
import org.tensorflow.lite.support.image.ops.ResizeWithCropOrPadOp;
import org.tensorflow.lite.support.image.ops.Rot90Op;
import org.tensorflow.lite.support.label.TensorLabel;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URLEncoder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.concurrent.FutureTask;

import okhttp3.MultipartBody;


public class MainActivity extends AppCompatActivity {

    String modelFile = "model.tflite";
    String ImageFile = "L4.jpg";
    String url = "http://123.57.0.181:5000/handle_image/";
    String post_url = "http://123.57.0.181:5000/score/";
    private Interpreter interpreter;
    private final int imageSizeX=1024;
    private final int imageSizeY=1024;
    private TensorImage image = new TensorImage();
    private static final float IMAGE_MEAN = 127.5f;
    private static final float IMAGE_STD = 127.5f;

    private static final float PROBABILITY_MEAN = 0.0f;

    private static final float PROBABILITY_STD = 1.0f;
    private final Interpreter.Options tfliteOptions = new Interpreter.Options();

    private List<String> labels = new ArrayList<String>();


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        TextView textView = findViewById(R.id.main_info);
        try {
            interpreter = new Interpreter( FileUtil.loadMappedFile(this, "model.tflite"), tfliteOptions);
        }
        catch (IOException e) {
            textView.setText("ok");
        }

        labels.add("wire_opening");
        labels.add("nest");
        labels.add("grass");


        textView.setText("Success loaded");

        AssetManager assetManager = this.getAssets();

    }

    public void analyze(View view){

        Picasso.get().load(url).into(new Target() {
            @Override
            public void onBitmapLoaded(Bitmap bitmap, Picasso.LoadedFrom loadedFrom) {
                TextView textView = findViewById(R.id.main_info);
                int cls_prob_index = 0;
                TensorImage InputImageBuffer = loadImage(bitmap);
                textView.setText("download success");
                try {
                    if (interpreter == null) {
                        textView.setText("null model");
                    } else {
                        int[] cls_prob_shape = interpreter.getOutputTensor(cls_prob_index).shape();


                        DataType prob_data_type = interpreter.getOutputTensor(cls_prob_index).dataType();
                        TensorBuffer cls_prob_out_buffer = TensorBuffer.createFixedSize(cls_prob_shape, prob_data_type);

                        TensorProcessor cls_prob_processor = new TensorProcessor.Builder().add(getPostprocessNormalizeOp()).build();

                        interpreter.run(InputImageBuffer.getBuffer(), cls_prob_out_buffer.getBuffer().rewind());

                        Map<String, Float> labeledProbability = new TensorLabel(labels, cls_prob_processor.process(cls_prob_out_buffer)).getMapWithFloatValue();


                        String res_string = "{";
                        float total = 0;
                        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
                            total += entry.getValue();

                        }

                        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
                            res_string += entry.getKey() + ":" + entry.getValue() * 100 / total + ",";
                        }


                        res_string += "}";
                        textView.setText(res_string);

                        AsyncHttpPost post = new AsyncHttpPost(post_url);
                        MultipartFormDataBody body = new MultipartFormDataBody();


                        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
                            body.addStringPart(entry.getKey(), entry.getValue().toString());

                        }

                        post.setBody(body);
                        AsyncHttpClient.getDefaultInstance().executeString(post, new AsyncHttpClient.StringCallback(){
                            @Override
                            public void onCompleted(Exception ex, AsyncHttpResponse source, String result) {
                                if (ex != null) {
                                    ex.printStackTrace();
                                    return;
                                }
                            }
                        });


                    }
                } catch (Exception e) {
                    textView.setText(e.toString());
                }

            }

            @Override
            public void onBitmapFailed(Exception e, Drawable drawable) {

            }

            @Override
            public void onPrepareLoad(Drawable drawable) {

            }
        });


    }

    private  Bitmap getBitmapFromURL(String src) {

        TextView textView = findViewById(R.id.main_info);
        try{
            java.net.URL url = new java.net.URL(src);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setDoInput(true);
            connection.connect();

            InputStream input = connection.getInputStream();
            Bitmap myBitmap = BitmapFactory.decodeStream(input);
            return myBitmap;
        }catch (Exception e){
            textView.setText(e.toString());
            return null;
        }
    }
    private MappedByteBuffer loadModelFile(Activity activity, String MODEL_FILE) throws IOException {
        AssetFileDescriptor fileDescriptor = activity.getAssets().openFd(MODEL_FILE);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    private Bitmap getImage(Activity activity, String filepath){
        AssetManager assetManager = activity.getAssets();
        InputStream istr;
        Bitmap bitmap = null;
        try{
            istr = assetManager.open(filepath);
            bitmap = BitmapFactory.decodeStream(istr);
        }catch (IOException e){

        }
        return bitmap;
    }

    private TensorImage loadImage(final Bitmap bitmap){
        image.load(bitmap);

        int cropSize = Math.min(bitmap.getWidth(), bitmap.getHeight());
        ImageProcessor imageProcessor =
                new ImageProcessor.Builder()
                                  .add(new ResizeWithCropOrPadOp(cropSize, cropSize))
                                  .add(new ResizeOp(imageSizeX, imageSizeY, ResizeMethod.BILINEAR))
                                  .add(getPreprocessNormalizeOp())
                                  .build();

        return imageProcessor.process(image);

    }



    protected TensorOperator getPreprocessNormalizeOp() {
        return new NormalizeOp(IMAGE_MEAN, IMAGE_STD);
    }

    protected TensorOperator getPostprocessNormalizeOp() {
        return new NormalizeOp(PROBABILITY_MEAN, PROBABILITY_STD);
    }

}
