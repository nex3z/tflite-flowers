package com.nex3z.flowers.classification.ui.camera

import android.os.Bundle
import android.util.DisplayMetrics
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.camera.core.AspectRatio
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.Navigation
import androidx.navigation.fragment.findNavController
import com.nex3z.flowers.classification.R
import com.nex3z.flowers.classification.util.hasCameraPermissions
import kotlinx.android.synthetic.main.camera_fragment.*
import timber.log.Timber
import java.util.concurrent.Executors
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

class CameraFragment : Fragment() {

    private lateinit var viewModel: CameraViewModel
    private val executor = Executors.newSingleThreadExecutor()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?,
                              savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.camera_fragment, container, false)
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        viewModel = ViewModelProvider(this).get(CameraViewModel::class.java)
    }

    override fun onResume() {
        super.onResume()
        if (!hasCameraPermissions(requireContext())) {
            findNavController().navigate(R.id.action_camera_to_permission)
        } else {
            bindCamera()
        }
    }

    private fun bindCamera() = pv_cf_view_finder.post {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
        cameraProviderFuture.addListener(Runnable {
            val metrics = DisplayMetrics().also { pv_cf_view_finder.display.getRealMetrics(it) }
            val ratio = aspectRatio(metrics.widthPixels, metrics.heightPixels)
            val rotation = pv_cf_view_finder.display.rotation
            Timber.d("bindCamera(): metrics = $metrics, ratio = $ratio, rotation = $rotation")

            val cameraProvider = cameraProviderFuture.get()

            val cameraSelector = CameraSelector.Builder()
                .requireLensFacing(CameraSelector.LENS_FACING_BACK)
                .build()

            val preview = Preview.Builder()
                .setTargetAspectRatio(ratio)
                .setTargetRotation(rotation)
                .build()

            val imageAnalysis = ImageAnalysis.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_4_3)
                .setTargetRotation(rotation)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(executor, ImageAnalysis.Analyzer { image ->
                        image.close()
                    })
                }

            cameraProvider.unbindAll()

            try {
                val camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalysis)
                Timber.i("bindCamera(): sensorRotationDegrees = ${camera.cameraInfo.sensorRotationDegrees}")
                preview.setSurfaceProvider(pv_cf_view_finder.createSurfaceProvider())
            } catch (e: Exception) {
                Timber.e(e, "bindCamera(): Failed to bind use cases")
            }
//            Timber.v("imageAnalysis.attachedSurfaceResolution = ${imageAnalysis.attachedSurfaceResolution}")
//            Timber.v("preview.attachedSurfaceResolution = ${preview.attachedSurfaceResolution}")
        }, ContextCompat.getMainExecutor(requireContext()))
    }

    companion object {
        private const val RATIO_4_3_VALUE = 4.0 / 3.0
        private const val RATIO_16_9_VALUE = 16.0 / 9.0

        fun aspectRatio(width: Int, height: Int): Int {
            val previewRatio = max(width, height).toDouble() / min(width, height)
            if (abs(previewRatio - RATIO_4_3_VALUE) <= abs(previewRatio - RATIO_16_9_VALUE)) {
                return AspectRatio.RATIO_4_3
            }
            return AspectRatio.RATIO_16_9
        }
    }
}