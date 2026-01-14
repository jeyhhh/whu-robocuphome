/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define EncoderCounterOneCirCle 396
#define ENCODER_COUNTER_ONE_ANGLE      (EncoderCounterOneCirCle / 360.0f)
#define MOTOR_MAX_SPEED     100
#define MOTOR_MIN_SPEED     -100
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;

UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_USB_DEVICE_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
	// ������ʱ��3�жϣ�10ms��ʱ�жϣ�
	HAL_TIM_Base_Start_IT(&htim3);

	// �����������ӿڣ�TIM2�� - ����Ҫ�жϣ�ֻ������������ģʽ
	HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);

	// ����PWM�����TIM4ͨ��3�� - ����Ҫ�ж�
	HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_3);
	// ���ʹ������PWMͨ����Ҳ����ͨ��4��
	// HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_4);

	// ���ó�ʼ״̬�����ֹͣ
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);  // ����1��
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);  // ����2��

	// ���ó�ʼPWMռ�ձ�Ϊ0��ֹͣ��
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 0);
	
	Encoder_Init();
	Motor_Init();
	
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	Encoder_RunNrad(3,0);
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 0;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 0;
  if (HAL_TIM_Encoder_Init(&htim2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 7199;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 99;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 71;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 999;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_PWM_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim4, &sConfigOC, TIM_CHANNEL_3) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim4, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */
  HAL_TIM_MspPostInit(&htim4);

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2|GPIO_PIN_3, GPIO_PIN_RESET);

  /*Configure GPIO pins : PA2 PA3 */
  GPIO_InitStruct.Pin = GPIO_PIN_2|GPIO_PIN_3;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
// ȫ�ֱ�������
int32_t Encode_Target = 0;             // ����Ŀ��λ����Ϣ
int32_t EncoderLeftCounter = 0;        // ���浱ǰλ����Ϣ
int32_t SpeedLeft = 0;                 // ��������ٶ���Ϣ

void Motor_Init(void)
{
    // ע�⣺CubeMX���Զ�����TIM4��GPIO�ĳ�ʼ������
    // ����ֻ������PWMͨ��
    
    // ����PWMͨ��3��������
    HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_3);
    
    // ���ʹ�����������Ҳ����ͨ��4���ҵ����
    // HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_4);
    
    // ���ó�ʼ��������״̬
    // ע�⣺ԭ����ʹ��GPIOE0��GPIOE1���������ʹ��PA2��PA3
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);  // ����1��ʼ��
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);  // ����2��ʼ��
    
    // ���ó�ʼPWMռ�ձ�Ϊ0��ֹͣ��
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 0);
    // __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, 0);
}

/*********************************************************************
 *  �������ƣ�Motor_Speed(int PwmLeft, int PwmRight)
 *  �������ܣ����Ƶ���ٶ�
 *  ��    �Σ�PwmLeft: �����ٶȣ�-100��100��
 *            PwmRight: �ҵ���ٶȣ�-100��100��
 *  ��    ������
 *  ��    ע������HAL������Ӳ������
 ********************************************************************/
void Motor_Speed(int PwmLeft, int PwmRight)
{
    int32_t pwm_value_left, pwm_value_right;
    
    /* ========== �������� ========== */
    // �����ٶȷ�Χ
    if(PwmLeft > MOTOR_MAX_SPEED) PwmLeft = MOTOR_MAX_SPEED;
    if(PwmLeft < MOTOR_MIN_SPEED) PwmLeft = MOTOR_MIN_SPEED;
    
    // ����ԭ�����߼�����PWMֵ
    // ԭ���룺��תʱ (100 - PwmLeft) * 10
    //        ��תʱ (100 + PwmLeft) * 10
    if(PwmLeft > 0) {
        // ��ת
        pwm_value_left = (100 - PwmLeft) * 10;
        
        // ���÷���GPIOE0 = 0��ԭ���룩
        // ������ã�PA2 = 0, PA3 = 0����ת�߼���Ҫ�������Ӳ��ȷ����
        // ������ת��PA2 = 1, PA3 = 0
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_SET);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    }
    else if(PwmLeft < 0) {
        // ��ת
        pwm_value_left = (100 + PwmLeft) * 10;  // PwmLeft�Ǹ���������ʵ����100 - |PwmLeft|
        
        // ���÷���GPIOE0 = 1��ԭ���룩
        // ������ã�PA2 = 0, PA3 = 1����ת�߼���Ҫ�������Ӳ��ȷ����
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);
    }
    else {
        // ֹͣ
        pwm_value_left = 0;
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    }
    
    // ����PWMֵ��0-1000��Χ�ڣ���ΪTIM4��ARR=999��
    if(pwm_value_left < 0) pwm_value_left = 0;
    if(pwm_value_left > 1000) pwm_value_left = 1000;
    
    // ����PWMռ�ձȣ�ʹ��ͨ��3��
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, pwm_value_left);
    
    /* ========== �ҵ������ ========== */
    // ע�⣺������ϵͳֻ��һ�����������ע�͵��ⲿ��
    /*
    // �����ٶȷ�Χ
    if(PwmRight > MOTOR_MAX_SPEED) PwmRight = MOTOR_MAX_SPEED;
    if(PwmRight < MOTOR_MIN_SPEED) PwmRight = MOTOR_MIN_SPEED;
    
    if(PwmRight > 0) {
        // ��ת
        pwm_value_right = (100 - PwmRight) * 10;
        
        // ���÷���GPIOE1 = 0��ԭ���룩
        // ������ã�������ҵ������Ҫ����GPIO
        // HAL_GPIO_WritePin(�ҷ���1_GPIO, �ҷ���1_PIN, GPIO_PIN_RESET);
        // HAL_GPIO_WritePin(�ҷ���2_GPIO, �ҷ���2_PIN, GPIO_PIN_RESET);
    }
    else if(PwmRight < 0) {
        // ��ת
        pwm_value_right = (100 + PwmRight) * 10;
        
        // ���÷���GPIOE1 = 1��ԭ���룩
        // HAL_GPIO_WritePin(�ҷ���1_GPIO, �ҷ���1_PIN, GPIO_PIN_SET);
        // HAL_GPIO_WritePin(�ҷ���2_GPIO, �ҷ���2_PIN, GPIO_PIN_RESET);
    }
    else {
        // ֹͣ
        pwm_value_right = 0;
        // HAL_GPIO_WritePin(�ҷ���1_GPIO, �ҷ���1_PIN, GPIO_PIN_RESET);
        // HAL_GPIO_WritePin(�ҷ���2_GPIO, �ҷ���2_PIN, GPIO_PIN_RESET);
    }
    
    // ����PWMֵ
    if(pwm_value_right < 0) pwm_value_right = 0;
    if(pwm_value_right > 1000) pwm_value_right = 1000;
    
    // ����PWMռ�ձȣ�ʹ��ͨ��4��
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, pwm_value_right);
    */
}

/*********************************************************************
 *  �������ƣ�void Motor_Stop(void)
 *  �������ܣ�ֹͣ���
 *  ��    �Σ���
 *  ��    ������
 *  ��    ע����
 ********************************************************************/
void Motor_Stop(void)
{
    // ֹͣ����
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 0);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    
    // ֹͣ�ҵ�������ʹ�ã�
    // __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, 0);
}

/*********************************************************************
 *  �������ƣ�void Encoder_CountInit
 *  �������ܣ��������������ų�ʼ��
 *  ��    �Σ���
 *  ��    ������
 *  ��    ע������HAL�⣬CubeMX������TIM2Ϊ������ģʽ
 ********************************************************************/
void Encoder_CountInit(void)
{
    // ע�⣺CubeMX���Զ�����TIM2�ĳ�ʼ�����루MX_TIM2_Init��
    // ����ֻ�������������ӿ�
    
    // ����������ģʽ��ʹ��HAL�⺯����
    HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
    
    // ���ó�ʼ����ֵΪ0
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    
    // ������±�־λ
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    
    // �����Ҫ����������жϣ��������ã���ͨ������Ҫ��
    // __HAL_TIM_ENABLE_IT(&htim2, TIM_IT_UPDATE);
}

/*********************************************************************
 *  �������ƣ�void Encoder_TimInit
 *  �������ܣ���������ʱ��ʼ��
 *  ��    �Σ���
 *  ��    ������
 *  ��    ע��ʹ��TIM3��Ϊ10ms��ʱ�жϣ�CubeMX������
 ********************************************************************/
void Encoder_TimInit(void)
{
    // ע�⣺CubeMX���Զ�����TIM3�ĳ�ʼ�����루MX_TIM3_Init��
    // ����ֻ��������ʱ���ж�
    
    // ����TIM3������ʱ���������ж�
    HAL_TIM_Base_Start_IT(&htim3);
    
    // �����Ҫ���������ó�ʼ�ж�״̬Ϊ����
    // ��ͨ����ʼ��������ã�����Ҫʱ��ͨ��Encoder_RunNrad����
}

/*********************************************************************
 *  �������ƣ�void Encoder_Init
 *  �������ܣ���������ʼ��
 *  ��    �Σ���
 *  ��    ������
 *  ��    ע����ʼ�������������Ͷ�ʱ��
 ********************************************************************/
void Encoder_Init(void)
{
    Encoder_CountInit();
    Encoder_TimInit();
    
    // ��ʼ����̬����
    Encode_Target = 0;
    EncoderLeftCounter = 0;
    SpeedLeft = 0;
}

/*********************************************************************
 *  �������ƣ�void Encoder_RunNrad(int circle, int angle)
 *  �������ܣ��趨��������Ŀ��λ�ã����򿪱�������ʱ�ж�
 *  ��    �Σ�circle:����ת��Ȧ��
 *            angle������ת���Ƕ�
 *  ��    ������
 *  ��    ע������Ŀ��λ�ò����ÿ���
 ********************************************************************/
void Encoder_RunNrad(int circle, int angle)
{
    // ���ó�ʼλ�ã�ԭ��������Ϊ30000�����ﱣ��ԭ�߼���
    Encode_Target = 30000;
    __HAL_TIM_SET_COUNTER(&htim2, 30000);
    
    // ����Ŀ��λ�ã�����Ȧ���ͽǶȶ�Ӧ����������
    Encode_Target += circle * EncoderCounterOneCirCle;
    Encode_Target += (int32_t)(angle * ENCODER_COUNTER_ONE_ANGLE);
    
    // ���ö�ʱ���жϣ���ʼ���ƣ�
    // ע�⣺TIM3�ж���Encoder_TimInit��������������ֻ��ȷ��������
}

/*********************************************************************
 *  �������ƣ�int Position_Right_PID(void)
 *  �������ܣ�λ��PID���ƺ���
 *  ��    �Σ���
 *  ��    ����PID���ֵ
 *  ��    ע����ֲԭ����PID�㷨
 ********************************************************************/
int32_t Position_Right_PID(void)
{   
    // PID����������ԭ���������
    int32_t Position_KP = -5, Position_KI = 0, Position_KD = 0;
    static int32_t Bias, Pwm, Integral_bias, Last_Bias;
    
    // ����ƫ��
    Bias = Encode_Target - EncoderLeftCounter;
    
    // �������ֹ���ֱ��ͣ�
    Integral_bias += Bias;
    if(Integral_bias > 10000) Integral_bias = 10000;
    if(Integral_bias < -10000) Integral_bias = -10000;
    
    // λ��ʽPID������
    Pwm = Position_KP * Bias + Position_KI * Integral_bias + Position_KD * (Bias - Last_Bias);
    Last_Bias = Bias;  // ������һ��ƫ��
    
    // ����޷�
    if(Pwm > 20) Pwm = 20;
    if(Pwm < -20) Pwm = -20;
    
    return Pwm;  // �������
}

/*********************************************************************
 *  �������ƣ�void Encoder_Update(void)
 *  �������ܣ����������º�������TIM3�ж��е���
 *  ��    �Σ���
 *  ��    ������
 *  ��    ע��ÿ10msִ��һ�Σ�����λ�á��ٶȲ�ִ��PID����
 ********************************************************************/
void Encoder_Update(void)
{
    static int32_t EncoderLeftLast = 0;
    int32_t pwm_temp = 0;
    
    // ��ȡ��ǰλ��
    EncoderLeftCounter = __HAL_TIM_GET_COUNTER(&htim2);
    
    // ����ʵ���ٶȣ�ԭ����ֱ��ʹ�ò�ֵ��������ʱ�䣩
    SpeedLeft = EncoderLeftCounter - EncoderLeftLast;
    EncoderLeftLast = EncoderLeftCounter;
    
    // ����ʵ��λ�ü���PID���
    pwm_temp = Position_Right_PID();
    
    // ���Ƶ����ԭ�������Motor_Speed��������Ҫ������ĵ�����ƺ�����
    // ע�⣺ԭ����Motor_Speed����������������ٶȣ�������Ҫ����ʵ������޸�
    Motor_Speed(pwm_temp, pwm_temp);  // ԭ����
    
    // ʹ����ĵ�����ƺ�������������һ��Motor_SetSpeed����
    // ��Ҫ����pwm_temp���������÷�����ٶ�
    
    // �ж��Ƿ񵽴�Ŀ��λ��
    if(((Encode_Target - EncoderLeftCounter < 20) && (Encode_Target - EncoderLeftCounter > 0)) 
        || ((EncoderLeftCounter - Encode_Target < 20) && (EncoderLeftCounter - Encode_Target > 0)))
    {
        // ����Ŀ��λ�ã�ֹͣ���
        // Motor_Speed(0, 0);  // ԭ����
        
        // ʹ�����ֹͣ����
        Motor_Speed(0, 0);  // ��Ҫ��ʵ���������
        
        // ����ԭ��������˶�ʱ���жϣ������Ǳ����ж����У�ֻ��ֹͣ���
        // �������Ҫ�����жϣ����ԣ�
        // HAL_TIM_Base_Stop_IT(&htim3);
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM3)  // 10ms�ж�
    {
        // ���ñ��������º���
        Encoder_Update();
    }
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
