/**
 * Ejemplo de integración con Android (Kotlin)
 * Cliente API para el sistema IBEX 35 Trading
 * 
 * Dependencias necesarias en build.gradle:
 * 
 * dependencies {
 *     implementation 'com.squareup.retrofit2:retrofit:2.9.0'
 *     implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
 *     implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
 *     implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
 * }
 */

package com.example.ibex35trading.api

import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

// ================ DATA CLASSES ================

data class RankingResponse(
    val total: Int,
    val sector_filter: String?,
    val min_score_filter: Float?,
    val timestamp: String,
    val ranking: List<StockRanking>
)

data class StockRanking(
    val symbol: String,
    val name: String,
    val sector: String,
    val score: Float,
    val rating: String,
    val confidence: String,
    val price: Float,
    val change_pct: Float,
    val technical_score: Float,
    val momentum_score: Float,
    val sentiment_score: Float
)

data class StockScoreResponse(
    val symbol: String,
    val name: String,
    val sector: String,
    val timestamp: String,
    val price: Float,
    val score: Float,
    val rating: String,
    val confidence: String,
    val sub_scores: SubScores,
    val signals: List<String>,
    val indicators: Indicators
)

data class SubScores(
    val technical: Float,
    val momentum: Float,
    val sentiment: Float
)

data class Indicators(
    val rsi: Float?,
    val macd: Float?,
    val macd_signal: Float?,
    val sma_20: Float?,
    val sma_50: Float?
)

data class SignalResponse(
    val symbol: String,
    val name: String,
    val strategy: String,
    val timestamp: String,
    val signal: String,
    val confidence: Float,
    val reason: String,
    val current_price: Float,
    val stop_loss: Float?,
    val take_profit: Float?,
    val risk_reward: Float?
)

data class BacktestResponse(
    val symbol: String,
    val name: String,
    val strategy: String,
    val timestamp: String,
    val initial_capital: Float,
    val final_equity: Float,
    val metrics: BacktestMetrics,
    val recent_trades: List<Trade>
)

data class BacktestMetrics(
    val total_trades: Int,
    val winning_trades: Int,
    val losing_trades: Int,
    val win_rate: Float,
    val total_return: Float,
    val total_return_pct: Float,
    val max_drawdown: Float,
    val sharpe_ratio: Float,
    val avg_win: Float,
    val avg_loss: Float,
    val profit_factor: Float
)

data class Trade(
    val entry_date: String,
    val entry_price: Float,
    val exit_date: String?,
    val exit_price: Float?,
    val profit_loss: Float?,
    val profit_loss_pct: Float?,
    val reason: String
)

// ================ RETROFIT INTERFACE ================

interface IBEX35ApiService {
    
    @GET("/api/v1/ibex35/ranking")
    suspend fun getRanking(
        @Query("limit") limit: Int = 35,
        @Query("sector") sector: String? = null,
        @Query("min_score") minScore: Float? = null
    ): Response<RankingResponse>
    
    @GET("/api/v1/stock/{symbol}/score")
    suspend fun getStockScore(
        @Path("symbol") symbol: String
    ): Response<StockScoreResponse>
    
    @GET("/api/v1/stock/{symbol}/signals")
    suspend fun getStockSignals(
        @Path("symbol") symbol: String,
        @Query("strategy") strategy: String = "ensemble"
    ): Response<SignalResponse>
    
    @GET("/api/v1/stock/{symbol}/backtest")
    suspend fun getBacktest(
        @Path("symbol") symbol: String,
        @Query("strategy") strategy: String = "ensemble",
        @Query("initial_capital") initialCapital: Float = 10000f
    ): Response<BacktestResponse>
    
    @GET("/api/v1/watchlist")
    suspend fun getWatchlist(
        @Query("min_score") minScore: Float = 7.0f
    ): Response<RankingResponse>
}

// ================ API CLIENT ================

object IBEX35ApiClient {
    
    // Cambiar por tu URL de producción
    private const val BASE_URL = "http://localhost:8000/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val api: IBEX35ApiService = retrofit.create(IBEX35ApiService::class.java)
}

// ================ REPOSITORY (opcional) ================

class IBEX35Repository {
    
    private val api = IBEX35ApiClient.api
    
    suspend fun getRanking(limit: Int = 35, sector: String? = null, minScore: Float? = null): Result<RankingResponse> {
        return try {
            val response = api.getRanking(limit, sector, minScore)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getStockScore(symbol: String): Result<StockScoreResponse> {
        return try {
            val response = api.getStockScore(symbol)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getStockSignals(symbol: String, strategy: String = "ensemble"): Result<SignalResponse> {
        return try {
            val response = api.getStockSignals(symbol, strategy)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getWatchlist(minScore: Float = 7.0f): Result<RankingResponse> {
        return try {
            val response = api.getWatchlist(minScore)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ================ EJEMPLO DE USO EN VIEWMODEL ================

/*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class IBEX35ViewModel : ViewModel() {
    
    private val repository = IBEX35Repository()
    
    private val _rankingState = MutableStateFlow<UiState<RankingResponse>>(UiState.Loading)
    val rankingState: StateFlow<UiState<RankingResponse>> = _rankingState
    
    private val _stockScoreState = MutableStateFlow<UiState<StockScoreResponse>>(UiState.Loading)
    val stockScoreState: StateFlow<UiState<StockScoreResponse>> = _stockScoreState
    
    fun loadRanking(limit: Int = 10, minScore: Float? = null) {
        viewModelScope.launch {
            _rankingState.value = UiState.Loading
            val result = repository.getRanking(limit, null, minScore)
            _rankingState.value = if (result.isSuccess) {
                UiState.Success(result.getOrNull()!!)
            } else {
                UiState.Error(result.exceptionOrNull()?.message ?: "Error desconocido")
            }
        }
    }
    
    fun loadStockScore(symbol: String) {
        viewModelScope.launch {
            _stockScoreState.value = UiState.Loading
            val result = repository.getStockScore(symbol)
            _stockScoreState.value = if (result.isSuccess) {
                UiState.Success(result.getOrNull()!!)
            } else {
                UiState.Error(result.exceptionOrNull()?.message ?: "Error desconocido")
            }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
*/

// ================ EJEMPLO DE USO EN ACTIVITY/FRAGMENT ================

/*
class MainActivity : AppCompatActivity() {
    
    private val viewModel: IBEX35ViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Observar ranking
        lifecycleScope.launch {
            viewModel.rankingState.collect { state ->
                when (state) {
                    is UiState.Loading -> {
                        // Mostrar loading
                    }
                    is UiState.Success -> {
                        // Actualizar UI con state.data.ranking
                        val topStocks = state.data.ranking
                        updateRankingList(topStocks)
                    }
                    is UiState.Error -> {
                        // Mostrar error
                        Toast.makeText(this@MainActivity, state.message, Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
        
        // Cargar ranking inicial
        viewModel.loadRanking(limit = 10, minScore = 6.0f)
    }
    
    private fun updateRankingList(stocks: List<StockRanking>) {
        // Actualizar RecyclerView con los datos
    }
}
*/

// ================ EJEMPLO DE COMPOSABLE (JETPACK COMPOSE) ================

/*
@Composable
fun RankingScreen(viewModel: IBEX35ViewModel = viewModel()) {
    val state by viewModel.rankingState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadRanking()
    }
    
    when (val currentState = state) {
        is UiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UiState.Success -> {
            LazyColumn {
                items(currentState.data.ranking) { stock ->
                    StockItem(stock)
                }
            }
        }
        is UiState.Error -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Error: ${currentState.message}")
            }
        }
    }
}

@Composable
fun StockItem(stock: StockRanking) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(stock.name, style = MaterialTheme.typography.h6)
                Text("€${stock.price}", style = MaterialTheme.typography.h6)
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Score: ${stock.score}/10")
                Text(
                    stock.rating,
                    color = when {
                        stock.score >= 7 -> Color.Green
                        stock.score >= 5 -> Color.Blue
                        else -> Color.Red
                    }
                )
            }
            
            Text(
                "${stock.change_pct}%",
                color = if (stock.change_pct >= 0) Color.Green else Color.Red
            )
        }
    }
}
*/
