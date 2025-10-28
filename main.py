import traceback
from src.market_making import market_making

if __name__ == "__main__":
    try:
       market_making(max_order_size=100, min_order_size=10, num_orders=10, base_price_step_percentage=0.00009)
    except KeyboardInterrupt:
        print("Main process interrupted")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
