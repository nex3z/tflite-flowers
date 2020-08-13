package com.nex3z.flowers.classification.classifier

import android.content.Context
import android.graphics.Bitmap
import android.os.SystemClock
import org.tensorflow.lite.Delegate
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.nnapi.NnApiDelegate
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import timber.log.Timber
import java.io.Closeable

class Classifier(
    context: Context,
    private val model: Model,
    device: Device = Device.CPU,
    numThreads: Int = 4,
    private val topK: Int = 5
) {

    private val delegate: Delegate? = when(device) {
        Device.CPU -> null
        Device.NNAPI -> NnApiDelegate()
        Device.GPU -> GpuDelegate()
    }

    private val interpreter: Interpreter = Interpreter(
        FileUtil.loadMappedFile(context, model.fileName),
        Interpreter.Options().apply {
            setNumThreads(numThreads)
            delegate?.let { addDelegate(it) }
        }
    )

    private val inputBuffer: TensorImage =
        with(interpreter.getInputTensor(model.inputTensorIndex)) {
            TensorImage(dataType())
        }

    private val outputBuffer: TensorBuffer =
        with(interpreter.getOutputTensor(model.outputTensorIndex)) {
            TensorBuffer.createFixedSize(shape(), dataType())
        }

    fun classify(bitmap: Bitmap): List<Recognition> {
        inputBuffer.load(bitmap)
        return classify(inputBuffer)
    }

    fun classify(image: TensorImage): List<Recognition> {
        val img = model.imageProcessor.process(image)
        val start = SystemClock.uptimeMillis()
        interpreter.run(img.buffer, outputBuffer.buffer.rewind())
        val end = SystemClock.uptimeMillis()
        val timeCost = end - start
        val probs = model.postProcessor.process(outputBuffer).floatArray
        Timber.v("classify(): timeCost = $timeCost, probs = ${probs.contentToString()}")
        val recognitions: List<Recognition> = probs.mapIndexed(::Recognition)
        return recognitions.getTopK(topK)
    }

    fun close() {
        interpreter.close()
        if (delegate is Closeable) {
            delegate.close()
        }
    }
}
