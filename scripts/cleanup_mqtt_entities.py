"""清理 MQTT 中的旧实体配置，解决拼音命名问题。

运行此脚本将清除所有 MQTT retain 消息，让 HA 重新发现实体时使用正确的英文名称。
"""
import logging
import os
import time

import paho.mqtt.client as mqtt

from const import (
    BALANCE_SENSOR_NAME, DAILY_USAGE_SENSOR_NAME, YEARLY_USAGE_SENSOR_NAME,
    YEARLY_CHARGE_SENSOR_NAME, MONTH_USAGE_SENSOR_NAME, MONTH_CHARGE_SENSOR_NAME,
    MONTH_VALLEY_SENSOR_NAME, MONTH_FLAT_SENSOR_NAME, MONTH_PEAK_SENSOR_NAME,
    MONTH_TIP_SENSOR_NAME, PREPAY_BALANCE_SENSOR_NAME,
    STEP_USED_STEP1_SENSOR_NAME, STEP_REMAIN_STEP1_SENSOR_NAME,
    STEP_USED_STEP2_SENSOR_NAME, STEP_REMAIN_STEP2_SENSOR_NAME,
    STEP_USED_STEP3_SENSOR_NAME, STEP_TOTAL_USAGE_SENSOR_NAME,
    STEP_STAGE_SENSOR_NAME, load_project_env,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

load_project_env()


def cleanup_mqtt_entities():
    """清理所有 MQTT Discovery 配置，包括旧的拼音命名实体。"""
    mqtt_host = os.getenv("MQTT_HOST", "").strip()
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username = os.getenv("MQTT_USERNAME", "").strip()
    mqtt_password = os.getenv("MQTT_PASSWORD", "").strip()
    mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "ha_sgcc_electricity_cleanup").strip()
    mqtt_topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "homeassistant").strip()

    if not mqtt_host:
        logging.error("MQTT_HOST 未配置，无法执行清理")
        return False

    # 获取用户ID（用于清理特定用户的传感器）
    user_ids = os.getenv("LOGIN_TYPE_Indoor_ACCT_ID", "").strip().split(",")
    user_ids = [uid.strip() for uid in user_ids if uid.strip()]

    if not user_ids:
        logging.error("未配置 LOGIN_TYPE_INDOOR_ACCT_ID，无法确定要清理的用户")
        return False

    connected = False

    def on_connect(client, userdata, flags, reason_code, properties):
        nonlocal connected
        connected = True
        logging.info("MQTT 连接成功")

    try:
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_id,
        )
        client.on_connect = on_connect

        if mqtt_username and mqtt_password:
            client.username_pw_set(mqtt_username, mqtt_password)

        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()

        # 等待连接建立
        for _ in range(50):
            if connected:
                break
            time.sleep(0.1)

        if not connected:
            logging.error("MQTT 连接失败")
            return False

        sensor_bases = [
            BALANCE_SENSOR_NAME, DAILY_USAGE_SENSOR_NAME, YEARLY_USAGE_SENSOR_NAME,
            YEARLY_CHARGE_SENSOR_NAME, MONTH_USAGE_SENSOR_NAME, MONTH_CHARGE_SENSOR_NAME,
            MONTH_VALLEY_SENSOR_NAME, MONTH_FLAT_SENSOR_NAME, MONTH_PEAK_SENSOR_NAME,
            MONTH_TIP_SENSOR_NAME, PREPAY_BALANCE_SENSOR_NAME,
            STEP_USED_STEP1_SENSOR_NAME, STEP_REMAIN_STEP1_SENSOR_NAME,
            STEP_USED_STEP2_SENSOR_NAME, STEP_REMAIN_STEP2_SENSOR_NAME,
            STEP_USED_STEP3_SENSOR_NAME, STEP_TOTAL_USAGE_SENSOR_NAME,
            STEP_STAGE_SENSOR_NAME,
        ]

        cleaned_count = 0

        for user_id in user_ids:
            postfix = f"_{user_id[-4:]}"
            logging.info("清理用户 %s 的 MQTT 实体配置...", user_id)

            for base in sensor_bases:
                object_id = base.replace("sensor.", "") + postfix

                # 清理正确命名的配置（为了重新发现）
                config_topic = f"{mqtt_topic_prefix}/sensor/{object_id}/config"
                state_topic = f"{mqtt_topic_prefix}/sensor/{object_id}/state"
                attrs_topic = f"{mqtt_topic_prefix}/sensor/{object_id}/attributes"

                client.publish(config_topic, "", retain=True)
                client.publish(state_topic, "", retain=True)
                client.publish(attrs_topic, "", retain=True)

                # 清理旧版本（包含 sensor. 前缀）的配置
                legacy_topic = f"{mqtt_topic_prefix}/sensor/sensor.{object_id}/config"
                legacy_state = f"{mqtt_topic_prefix}/sensor/sensor.{object_id}/state"
                legacy_attrs = f"{mqtt_topic_prefix}/sensor/sensor.{object_id}/attributes"

                client.publish(legacy_topic, "", retain=True)
                client.publish(legacy_state, "", retain=True)
                client.publish(legacy_attrs, "", retain=True)

                cleaned_count += 1

        # 等待消息发送完成
        time.sleep(1)
        client.loop_stop()
        client.disconnect()

        logging.info("✅ 清理完成！共清理 %d 个传感器的配置", cleaned_count)
        logging.info("下一步操作：")
        logging.info("1. 在 Home Assistant 中删除拼音命名的实体（设置 > 设备与服务 > 实体）")
        logging.info("2. 重启本服务，让它重新发送正确的 MQTT Discovery 配置")
        logging.info("3. HA 会自动创建正确的英文命名实体")

        return True

    except Exception as e:
        logging.error("清理失败: %s", e)
        return False


if __name__ == "__main__":
    logging.info("开始清理 MQTT 实体配置...")
    cleanup_mqtt_entities()
